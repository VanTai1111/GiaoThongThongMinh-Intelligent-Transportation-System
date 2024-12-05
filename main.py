from tkinter import filedialog, Button, Label,Text, Scrollbar, Canvas
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO

class_translation = {
    "car": "ô tô",
    "motorcycle": "xe máy",
    "bus": "xe buýt",
    "truck": "xe tải",
    "bicycle": "xe đạp",
    "person": "người",
}

# Hàm chọn ảnh từ máy tính
def select_image(image_number):
    image_path = filedialog.askopenfilename(title="Chọn ảnh", filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    
    if not image_path:
        messagebox.showerror("Lỗi", "Không có ảnh nào được chọn.")
        return
    
    global images, resized_images
    images[image_number - 1] = cv2.imread(image_path)
    
    if images[image_number - 1] is None:
        messagebox.showerror("Lỗi", "Không thể đọc ảnh. Kiểm tra lại đường dẫn ảnh.")
        return
    
    # Resize ảnh
    new_width = 400
    aspect_ratio = images[image_number - 1].shape[1] / images[image_number - 1].shape[0]
    new_height = int(new_width / aspect_ratio)
    resized_images[image_number - 1] = cv2.resize(images[image_number - 1], (new_width, new_height))
    
    resized_image_rgb = cv2.cvtColor(resized_images[image_number - 1], cv2.COLOR_BGR2RGB)
    image_tk = ImageTk.PhotoImage(image=Image.fromarray(resized_image_rgb))
    image_labels[image_number - 1].config(image=image_tk)
    image_labels[image_number - 1].image = image_tk

# Hàm chọn vùng ROI và xử lý ảnh
def process_image(image_number):
    global resized_images, model
    
    image_resized = resized_images[image_number - 1]
    roi = cv2.selectROI(f"Select ROI for Image {image_number}", image_resized)
    
    if roi == (0, 0, 0, 0):
        messagebox.showinfo("Thông báo", "Không có vùng ROI được chọn.")
        return
    
    x, y, w, h = roi
    im_cropped = image_resized[y:y+h, x:x+w]

    results = model(im_cropped)
    
    def filter_results(results):
        """Lọc bỏ lớp 'person'."""
        filtered_results = results[0]
        keep_indices = [i for i, cls in enumerate(filtered_results.boxes.cls) 
                        if model.names[int(cls)] != "person"]
        filtered_results.boxes = filtered_results.boxes[keep_indices]
        return filtered_results

    # Lọc kết quả để bỏ lớp 'person'
    filtered_results = filter_results(results)
    
    def count_objects(results):
        counts = {}
        total_time = 0
        for cls in results.boxes.cls:
            class_name = model.names[int(cls)]
            class_name_vn = class_translation.get(class_name, class_name)
            counts[class_name_vn] = counts.get(class_name_vn, 0) + 1
            if class_name == "motorcycle":
                total_time += 2
            elif class_name == "car":
                total_time += 3
            else:
                total_time += 5
        return counts, total_time

    object_counts, total_time = count_objects(filtered_results)
    annotated_image = filtered_results.plot()

    annotated_image_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    annotated_image_pil = Image.fromarray(annotated_image_rgb)
    annotated_image_tk = ImageTk.PhotoImage(image=annotated_image_pil)

    image_labels[image_number - 1].config(image=annotated_image_tk)
    image_labels[image_number - 1].image = annotated_image_tk

    # Cập nhật kết quả vào vùng text
    result_texts[image_number - 1].delete(1.0, "end")
    result_texts[image_number - 1].insert("end", f"Số lượng phương tiện:\n")
    for class_name, count in object_counts.items():
        result_texts[image_number - 1].insert("end", f"{class_name}: {count}\n")
    
    # Lưu thời gian cho ảnh 1, 2, 3, 4
    if image_number == 1:
        total_time_for_image_1[0] = total_time
    elif image_number == 2:
        total_time_for_image_2[0] = total_time
    elif image_number == 3:
        total_time_for_image_3[0] = total_time
    elif image_number == 4:
        total_time_for_image_4[0] = total_time

    # Tính toán và hiển thị thời gian trung bình khi tất cả ảnh đã được xử lý
    if total_time_for_image_1[0] > 0 and total_time_for_image_3[0] > 0:
        avg_time_1_3 = (total_time_for_image_1[0] + total_time_for_image_3[0]) / 2
        result_texts[0].insert("end", f"\nSố giây đèn xanh: {avg_time_1_3:.2f} giây")
        result_texts[2].insert("end", f"\nSố giây đèn xanh: {avg_time_1_3:.2f} giây")  # Cập nhật khung ảnh 3
    
    if total_time_for_image_2[0] > 0 and total_time_for_image_4[0] > 0:
        avg_time_2_4 = (total_time_for_image_2[0] + total_time_for_image_4[0]) / 2
        result_texts[1].insert("end", f"\nSố giây đèn xanh: {avg_time_2_4:.2f} giây")
        result_texts[3].insert("end", f"\nSố giây đèn xanh: {avg_time_2_4:.2f} giây")  # Cập nhật khung ảnh 4


# Khởi tạo model YOLO
model = YOLO("yolo11n.pt")

# Khởi tạo danh sách ảnh và label
images = [None] * 4
resized_images = [None] * 4
image_labels = [None] * 4
result_texts = [None] * 4

# Biến lưu trữ tổng thời gian cho mỗi ảnh
total_time_for_image_1 = [0]
total_time_for_image_2 = [0]
total_time_for_image_3 = [0]
total_time_for_image_4 = [0]

# Tạo cửa sổ chính Tkinter
root = Tk()
root.title("Nhận diện phương tiện giao thông")
root.geometry("1000x700")

# Canvas để cuộn
main_canvas = Canvas(root, width=1000, height=700)
main_canvas.pack(side="left", fill="both", expand=True)

# Thanh cuộn cho canvas
scrollbar = Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side="right", fill="y")
main_canvas.config(yscrollcommand=scrollbar.set)

# Khung bên trong canvas để đặt các widget
scrollable_frame = Frame(main_canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)
main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Khung ảnh
frame = Frame(scrollable_frame, padx=10, pady=10)
frame.pack()

# Khởi tạo giao diện cho 4 ảnh
for i in range(4):
    # Hiển thị ảnh
    image_label = Label(frame)
    image_label.grid(row=i // 2 * 2, column=(i % 2) * 2, padx=10, pady=10)
    image_labels[i] = image_label

    # Hiển thị kết quả có thanh cuộn
    text_frame = Frame(frame)
    text_frame.grid(row=i // 2 * 2 + 1, column=(i % 2) * 2, padx=10, pady=10)

    result_scrollbar = Scrollbar(text_frame)
    result_scrollbar.pack(side="right", fill="y")

    result_text = Text(text_frame, width=40, height=10, wrap="word", yscrollcommand=result_scrollbar.set)
    result_text.pack(side="left", fill="both", expand=True)

    result_scrollbar.config(command=result_text.yview)
    result_texts[i] = result_text

# Khung nút
button_frame = Frame(scrollable_frame)
button_frame.pack(pady=20)

# Nút chọn và xử lý ảnh
for i in range(4):
    select_button = Button(button_frame, text=f"Chọn ảnh {i + 1}", command=lambda i=i: select_image(i + 1))
    select_button.grid(row=0, column=i, padx=10)

    process_button = Button(button_frame, text=f"Xử lý ảnh {i + 1}", command=lambda i=i: process_image(i + 1))
    process_button.grid(row=1, column=i, padx=10)

# Kích hoạt cuộn bằng chuột
def _on_mouse_wheel(event):
    main_canvas.yview_scroll(-1 * (event.delta // 120), "units")

main_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

root.mainloop()
