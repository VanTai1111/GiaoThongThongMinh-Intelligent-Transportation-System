from tkinter import Tk, filedialog, Button, Label, Text, Scrollbar, Canvas, Frame
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
    
    new_width = 400
    aspect_ratio = images[image_number - 1].shape[1] / images[image_number - 1].shape[0]
    new_height = int(new_width / aspect_ratio)
    resized_images[image_number - 1] = cv2.resize(images[image_number - 1], (new_width, new_height))
    
    resized_image_rgb = cv2.cvtColor(resized_images[image_number - 1], cv2.COLOR_BGR2RGB)
    image_tk = ImageTk.PhotoImage(image=Image.fromarray(resized_image_rgb))
    image_labels[image_number - 1].config(image=image_tk)
    image_labels[image_number - 1].image = image_tk

def update_traffic_light(canvas, state):
    """Cập nhật trạng thái đèn giao thông."""
    canvas.delete("all")
    colors = {"red": "gray", "yellow": "gray", "green": "gray"}
    colors[state] = state

    canvas.create_oval(10, 10, 60, 60, fill=colors["red"], outline="black")
    canvas.create_oval(10, 70, 60, 120, fill=colors["yellow"], outline="black")
    canvas.create_oval(10, 130, 60, 180, fill=colors["green"], outline="black")

# Biến toàn cục
remaining_green_time_1_3 = 0
remaining_yellow_time_1_3 = 3
remaining_red_time_1_3 = 0

remaining_green_time_2_4 = 0
remaining_yellow_time_2_4 = 3
remaining_red_time_2_4 = 0

def countdown_timer_1_3(green_time_1_3, text_widget, canvas):
    global remaining_green_time_1_3, helo, helo2
    # Giới hạn đèn xanh tối đa là 55 giây
    if green_time_1_3 > 55:
        green_time_1_3 = 55

    remaining_green_time_1_3 = green_time_1_3  # Lưu lại thời gian còn lại cho đèn xanh

    # Lưu giá trị đầu tiên vào biến `heloooooo`
    if 'helo' not in globals() and (total_time_for_image_1[0] > 0 or total_time_for_image_3[0] > 0):
        helo = remaining_green_time_1_3  # Gán giá trị chỉ khi `helo` chưa được tạo và có ảnh 1 hoặc 3

    # Hiển thị đèn xanh và thông báo
    update_traffic_light(canvas, "green")
    text_widget.delete(1.0, "end")
    text_widget.insert("end", f"Đèn xanh: {remaining_green_time_1_3} giây")

    if remaining_green_time_1_3 > 0:
        # Tiếp tục đếm ngược đèn xanh
        text_widget.after(1000, countdown_timer_1_3, remaining_green_time_1_3 - 1, text_widget, canvas)
    elif remaining_green_time_1_3 == 0:
        countdown_vyellow_1_3(remaining_yellow_time_1_3, text_widget, canvas)  # Chạy đèn vàng sau đèn xanh
        

def countdown_vyellow_1_3(remaining_yellow_1_3, text_widget, canvas):
    global remaining_yellow_time_1_3
    global remaining_red_time_1_3

    remaining_yellow_time_1_3 = remaining_yellow_1_3  # Lưu lại thời gian đèn vàng còn lại

    if remaining_yellow_time_1_3 > 0:
        state = "yellow"
        update_traffic_light(canvas, state)
        text_widget.delete(1.0, "end")
        text_widget.insert("end", f"Đèn vàng: {remaining_yellow_time_1_3} giây")
        text_widget.after(1000, countdown_vyellow_1_3, remaining_yellow_time_1_3 - 1, text_widget, canvas)
    else:
        remaining_red_time_1_3 = helo + 3  # Tính thời gian tổng đèn xanh + đèn vàng
        if remaining_red_time_1_3 > 60:
            remaining_red_time_1_3 = 60  # Giới hạn không quá 60 giây
        countdown_red_1_3(remaining_red_time_1_3, text_widget, canvas)

def countdown_red_1_3(remaining_red_time_1_3, text_widget, canvas):
    """
    Hiển thị đèn đỏ với đếm ngược trong khoảng thời gian tính toán.
    """
    if remaining_red_time_1_3 > 0:
        state = "red"
        update_traffic_light(canvas, state)
        text_widget.delete(1.0, "end")
        text_widget.insert("end", f"Đèn đỏ: {remaining_red_time_1_3} giây")
        text_widget.after(1000, countdown_red_1_3, remaining_red_time_1_3 - 1, text_widget, canvas)
    else:
        # Đèn đỏ kết thúc, hiển thị tắt trạng thái
        text_widget.delete(1.0, "end")
        text_widget.insert("end", "Đèn đỏ tắt")


# đèn _2_4
def countdown_timer_2_4(green_time_2_4, text_widget, canvas):
    global remaining_green_time_2_4, helo, helo2
    # Giới hạn đèn xanh tối đa là 55 giây
    if green_time_2_4 > 55:
        green_time_2_4 = 55

    remaining_green_time_2_4 = green_time_2_4  # Lưu lại thời gian còn lại cho đèn xanh

    # Lưu giá trị đầu tiên vào biến `heloooooo`
    if 'helo2' not in globals() and (total_time_for_image_2[0] > 0 or total_time_for_image_4[0] > 0):
        helo2 = remaining_green_time_2_4  # Gán giá trị chỉ khi `helo` chưa được tạo và có ảnh 2 hoặc 4

    # Hiển thị đèn xanh và thông báo
    update_traffic_light(canvas, "green")
    text_widget.delete(1.0, "end")
    text_widget.insert("end", f"Đèn xanh: {remaining_green_time_2_4} giây")

    if remaining_green_time_2_4 > 0:
        # Tiếp tục đếm ngược đèn xanh
        text_widget.after(1000, countdown_timer_2_4, remaining_green_time_2_4 - 1, text_widget, canvas)
    elif remaining_green_time_2_4 == 0:
        countdown_vyellow_2_4(remaining_yellow_time_2_4, text_widget, canvas)  # Chạy đèn vàng sau đèn xanh
        

def countdown_vyellow_2_4(remaining_yellow_2_4, text_widget, canvas):
    global remaining_yellow_time_2_4
    global remaining_red_time_2_4

    remaining_yellow_time_2_4 = remaining_yellow_2_4  # Lưu lại thời gian đèn vàng còn lại

    if remaining_yellow_time_2_4 > 0:
        state = "yellow"
        update_traffic_light(canvas, state)
        text_widget.delete(1.0, "end")
        text_widget.insert("end", f"Đèn vàng: {remaining_yellow_time_2_4} giây")
        text_widget.after(1000, countdown_vyellow_2_4, remaining_yellow_time_2_4 - 1, text_widget, canvas)
    else:
        remaining_red_time_2_4 = helo2 + 3  # Tính thời gian tổng đèn xanh + đèn vàng
        if remaining_red_time_2_4 > 60:
            remaining_red_time_2_4 = 60  # Giới hạn không quá 60 giây
        countdown_red_2_4(remaining_red_time_2_4, text_widget, canvas)

def countdown_red_2_4(remaining_red_time_2_4, text_widget, canvas):
    """
    Hiển thị đèn đỏ với đếm ngược trong khoảng thời gian tính toán.
    """
    if remaining_red_time_2_4 > 0:
        state = "red"
        update_traffic_light(canvas, state)
        text_widget.delete(1.0, "end")
        text_widget.insert("end", f"Đèn đỏ: {remaining_red_time_2_4} giây")
        text_widget.after(1000, countdown_red_2_4, remaining_red_time_2_4 - 1, text_widget, canvas)
    else:
        # Đèn đỏ kết thúc, hiển thị tắt trạng thái
        text_widget.delete(1.0, "end")
        text_widget.insert("end", "Đèn đỏ tắt")
        
def process_images_1_3():
    """
    Xử lý ảnh 1 và ảnh 3, tính toán thời gian cho đèn giao thông của ảnh 1_3.
    """
    if total_time_for_image_1[0] > 0 and total_time_for_image_3[0] > 0:
        avg_time_1_3 = (total_time_for_image_1[0] + total_time_for_image_3[0]) / 2
        countdown_timer_1_3(int(avg_time_1_3), result_texts[0], traffic_light_canvases[0])
        countdown_timer_1_3(int(avg_time_1_3), result_texts[2], traffic_light_canvases[0])
        
        messagebox.showinfo("Thông báo", "Hãy thêm ảnh 2_4 để xử lý")

def process_images_2_4():
    """
    Xử lý ảnh 2 và ảnh 4, tính toán thời gian cho đèn giao thông của ảnh 2_4.
    """
    if total_time_for_image_2[0] > 0 and total_time_for_image_4[0] > 0:
        avg_time_2_4 = (total_time_for_image_2[0] + total_time_for_image_4[0]) / 2
        countdown_timer_2_4(int(avg_time_2_4), result_texts[1], traffic_light_canvases[1])
        countdown_timer_2_4(int(avg_time_2_4), result_texts[3], traffic_light_canvases[1])
        
        messagebox.showinfo("Thông báo", "Hãy thêm ảnh 1_3 để xử lý")

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
        filtered_results = results[0]
        keep_indices = [i for i, cls in enumerate(filtered_results.boxes.cls) 
                        if model.names[int(cls)] != "person"]
        filtered_results.boxes = filtered_results.boxes[keep_indices]
        return filtered_results

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

    result_texts[image_number - 1].delete(1.0, "end")
    result_texts[image_number - 1].insert("end", f"Số lượng phương tiện:\n")
    for class_name, count in object_counts.items():
        result_texts[image_number - 1].insert("end", f"{class_name}: {count}\n")
    
    if image_number == 1:
        total_time_for_image_1[0] = total_time
        process_images_1_3()  # Gọi hàm xử lý ảnh 1 và 3 sau khi xử lý ảnh 1
    elif image_number == 2:
        total_time_for_image_2[0] = total_time
    elif image_number == 3:
        total_time_for_image_3[0] = total_time
        process_images_1_3()  # Gọi hàm xử lý ảnh 1 và 3 sau khi xử lý ảnh 3
    elif image_number == 4:
        total_time_for_image_4[0] = total_time
        process_images_2_4()  # Gọi hàm xử lý ảnh 2 và 4 sau khi xử lý ảnh 4

model = YOLO("yolo11n.pt")

images = [None] * 4
resized_images = [None] * 4
image_labels = [None] * 4
result_texts = [None] * 4
traffic_light_canvases = [None] * 2  # Chỉ 2 đèn giao thông

total_time_for_image_1 = [0]
total_time_for_image_2 = [0]
total_time_for_image_3 = [0]
total_time_for_image_4 = [0]

root = Tk()
root.title("Nhận diện phương tiện giao thông")
root.geometry("1200x700")  # Tăng chiều rộng để chứa đèn

main_canvas = Canvas(root, width=1200, height=700)
main_canvas.pack(side="left", fill="both", expand=True)

scrollbar = Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side="right", fill="y")
main_canvas.config(yscrollcommand=scrollbar.set)

scrollable_frame = Frame(main_canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)
main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

frame = Frame(scrollable_frame, padx=10, pady=10)
frame.pack()

for i in range(4):
    image_label = Label(frame)
    image_label.grid(row=i // 2 * 2, column=(i % 2) * 3, padx=10, pady=10)
    image_labels[i] = image_label

    text_frame = Frame(frame)
    text_frame.grid(row=i // 2 * 2 + 1, column=(i % 2) * 3, padx=10, pady=10)

    result_scrollbar = Scrollbar(text_frame)
    result_scrollbar.pack(side="right", fill="y")

    result_text = Text(text_frame, width=40, height=10, wrap="word", yscrollcommand=result_scrollbar.set)
    result_text.pack(side="left", fill="both", expand=True)

    result_scrollbar.config(command=result_text.yview)
    result_texts[i] = result_text

for i in range(2):
    traffic_light_canvas = Canvas(frame, width=70, height=200, bg="white")
    traffic_light_canvas.grid(row=i * 2, column=4, rowspan=2, padx=10, pady=10)
    traffic_light_canvases[i] = traffic_light_canvas

button_frame = Frame(scrollable_frame)
button_frame.pack(pady=20)

for i in range(4):
    select_button = Button(button_frame, text=f"Chọn ảnh {i + 1}", command=lambda i=i: select_image(i + 1))
    select_button.grid(row=0, column=i, padx=10)

    process_button = Button(button_frame, text=f"Xử lý ảnh {i + 1}", command=lambda i=i: process_image(i + 1))
    process_button.grid(row=1, column=i, padx=10)

def _on_mouse_wheel(event):
    main_canvas.yview_scroll(-1 * (event.delta // 120), "units")

# Khởi tạo đèn giao thông khi ứng dụng bắt đầu
def initialize_traffic_lights():
    for i in range(2):  # Chỉ có 2 đèn giao thông
        # Mặc định hiển thị đèn đỏ và thông báo "Đang xử lý"
        update_traffic_light(traffic_light_canvases[i], "red")
        result_texts[i].delete(1.0, "end")
        result_texts[i].insert("end", "Đang xử lý...")

# Gọi hàm khởi tạo khi ứng dụng mở
initialize_traffic_lights()

main_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

root.mainloop()
