# Hospital Management System

Hệ thống quản lý bệnh viện với microservices architecture sử dụng FastAPI, Flask và MongoDB.

## 🚀 Quick Start

### Cách 1: Script tự động

**MacOS/Linux:**
```bash
git clone <repository-url>
cd UDPT_HospitalManagementSystem
./quick-setup.sh
```

**Windows:**
```bash
git clone <repository-url>
cd UDPT_HospitalManagementSystem
quick-setup.bat
```

### Cách 2: Setup thủ công

Xem hướng dẫn chi tiết tại: [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🛠️ Tech Stack

- **Backend:** FastAPI + Motor (MongoDB async driver)
- **Frontend:** Flask + Jinja2 templates
- **Database:** MongoDB Atlas
- **Languages:** Python 3.9+

## 📁 Project Structure

```
services/patient-service/
├── backend/          # FastAPI API service
├── frontend/         # Flask web interface
└── run-all.py       # Script chạy cả 2 services
```

## 🌐 Access URLs

- **Web Interface:** http://127.0.0.1:5000
- **API Backend:** http://127.0.0.1:8001
- **API Docs:** http://127.0.0.1:8001/docs

## 📋 Features

- ✅ Quản lý thông tin bệnh nhân
- ✅ Tìm kiếm và lọc bệnh nhân
- ✅ RESTful API
- ✅ Responsive web interface
- ✅ MongoDB Atlas integration

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

Nếu gặp vấn đề, xem [SETUP_GUIDE.md](SETUP_GUIDE.md) hoặc tạo issue.

---

## 📋 Original SRS Document Content

FR-4: Quản lý Thanh toán & BHYT
FR-5: Quản lý Đơn thuốc
FR-6: Quản lý Thông báo
FR-7: Báo cáo và Thống kê
4. Yêu cầu Phi Chức năng (Non-Functional Requirements)
4.1. Yêu cầu về Hiệu năng
4.2. Yêu cầu về Bảo mật
4.3. Yêu cầu về Tính sẵn sàng & Tin cậy
4.4. Yêu cầu về Tính mở rộng
5. Yêu cầu về Giao diện
5.1. Giao diện Người dùng (UI)
5.2. Giao diện Hệ thống (API)
Mô tả chi tiết các thành phần
Actors (Tác nhân)
Use Cases chính
Các mối quan hệ trong diagram
Luồng quy trình chính
Tài liệu Đặc tả Yêu cầu (SRS)
Dự án: Hệ thống Quản lý Bệnh viện ABC Phiên bản: 1.0 Ngày: 05/08/2025

1. Giới thiệu
1.1. Mục đích
Tài liệu này đặc tả các yêu cầu chức năng và phi chức năng cho Hệ thống Quản lý Bệnh viện ABC. Mục tiêu là xây dựng một hệ thống theo kiến trúc Microservices để tối ưu hóa việc quản lý bệnh nhân, lịch khám, đơn thuốc và các quy trình liên quan, hỗ trợ cả hai luồng nghiệp vụ khám có BHYT và không có BHYT.

1.2. Bối cảnh dự án
Bệnh viện ABC đang đối mặt với sự gia tăng số lượng bệnh nhân, trong khi các quy trình quản lý hiện tại còn thủ công và thiếu hiệu quả. Ban giám đốc đã quyết định xây dựng một hệ thống quản lý hiện đại nhằm cải thiện dịch vụ, xử lý đồng thời nhiều yêu cầu, và đảm bảo giao tiếp hiệu quả giữa các bộ phận.

1.3. Định nghĩa & Viết tắt
BHYT: Bảo hiểm Y tế
CLS: Cận lâm sàng (các dịch vụ như xét nghiệm, chẩn đoán hình ảnh)
SRS: Software Requirements Specification (Tài liệu Đặc tả Yêu cầu)
API: Application Programming Interface (Giao diện lập trình ứng dụng)
2. Mô tả tổng quan
2.1. Chức năng chính của hệ thống
Hệ thống sẽ bao gồm các chức năng cốt lõi sau:

Quản lý bệnh nhân
Quản lý lịch khám
Quản lý đơn thuốc
Gửi thông báo
Báo cáo và thống kê
2.2. Tác nhân hệ thống
Hệ thống có các tác nhân chính sau:

Bệnh nhân: Sử dụng hệ thống để đặt lịch và theo dõi thông tin sức khỏe.
Bác sĩ: Sử dụng hệ thống để quản lý lịch khám, khám bệnh và kê đơn.
Quản trị viên: Quản lý toàn bộ hệ thống, người dùng và xem báo cáo.
Nhân viên (Lễ tân, Thu ngân, Dược sĩ): Sử dụng các chức năng tương ứng với vai trò của mình.
3. Yêu cầu Chức năng (Functional Requirements)
FR-1: Quản lý Bệnh nhân
FR-1.1: Hệ thống phải cho phép nhân viên lễ tân đăng ký thông tin cho bệnh nhân mới.
FR-1.2: Hệ thống phải cho phép tra cứu thông tin bệnh nhân đã có trong hệ thống qua các trường như số điện thoại, mã bệnh nhân, tên bệnh nhân(năm sinh) hoặc filter nhiều trường.
FR-1.3: Hệ thống phải lưu trữ hồ sơ bệnh án và lịch sử khám chữa bệnh của bệnh nhân.
FR-1.4: Hệ thống cho phép bệnh nhân đăng ký thông tin cho bệnh nhân mới.
FR-1.3 : Hệ thống cho phép bệnh nhân xem hồ sơ cá nhân, lịch sử khám bệnh
FR-2: Quản lý Lịch khám
FR-2.1: Hệ thống phải cho phép bệnh nhân hoặc nhân viên đặt lịch khám theo chuyên khoa hoặc theo bác sĩ cụ thể, hoặc theo ngày khám.
FR-2.2: Hệ thống phải cho phép bác sĩ xem và xác nhận lịch khám của mình.
FR-3: Quản lý Khám bệnh & Chỉ định Dịch vụ
FR-3.1: Hệ thống phải cho phép bác sĩ truy cập hồ sơ bệnh án của bệnh nhân trong quá trình khám.
FR-3.2: Hệ thống phải cho phép bác sĩ tạo các phiếu chỉ định dịch vụ CLS cho bệnh nhân.
FR-4: Quản lý Thanh toán & BHYT
FR-4.1: Hệ thống phải có khả năng kết nối với Cổng giám định BHYT để xác thực thông tin thẻ của bệnh nhân.
FR-4.2: (Luồng BHYT) Hệ thống phải tự động tính toán chi phí đồng chi trả mà bệnh nhân cần thanh toán cho phí khám, dịch vụ CLS và thuốc.
FR-4.3: (Luồng Dịch vụ) Hệ thống phải tính toán 100% chi phí dựa trên bảng giá dịch vụ niêm yết của bệnh viện.
FR-4.4: Hệ thống phải ghi nhận lại tất cả giao dịch thanh toán và xuất hóa đơn.
FR-5: Quản lý Đơn thuốc
FR-5.1: Hệ thống phải cho phép bác sĩ tạo đơn thuốc điện tử cho bệnh nhân sau khi khám.
FR-5.2: Hệ thống phải cho phép dược sĩ truy cập đơn thuốc và cập nhật trạng thái (ví dụ: đã lấy, chưa lấy) sau khi cấp phát.
FR-6: Quản lý Thông báo
FR-6.1: Hệ thống phải tự động gửi thông báo nhắc nhở lịch khám cho bệnh nhân qua Email hoặc SMS.
FR-6.2: Hệ thống phải gửi thông báo cho bệnh nhân khi đơn thuốc của họ đã sẵn sàng để lấy.
FR-7: Báo cáo và Thống kê
FR-7.1: Hệ thống phải cho phép quản trị viên thống kê số lượng bệnh nhân theo tháng.
FR-7.2: Hệ thống phải cho phép quản trị viên báo cáo số lượng đơn thuốc đã được cấp trong một khoảng thời gian.
4. Yêu cầu Phi Chức năng (Non-Functional Requirements)
4.1. Yêu cầu về Hiệu năng
NFR-1.1: Hệ thống phải có khả năng xử lý ít nhất 100 yêu cầu/giây, đặc biệt trong giờ cao điểm.
NFR-1.2: Độ trễ tối đa khi gọi API không được vượt quá 1 giây.
4.2. Yêu cầu về Bảo mật
NFR-2.1: Hệ thống phải có cơ chế xác thực (authentication) và phân quyền (authorization) chặt chẽ cho tất cả các vai trò người dùng.
NFR-2.2: Dữ liệu nhạy cảm của bệnh nhân (số điện thoại, email, thông tin sức khỏe) phải được mã hóa khi lưu trữ và truyền tải.
4.3. Yêu cầu về Tính sẵn sàng & Tin cậy
NFR-3.1: Các dịch vụ phải hoạt động độc lập. Nếu một dịch vụ gặp lỗi, các dịch vụ khác vẫn phải hoạt động bình thường để đảm bảo tính liên tục của hệ thống.
4.4. Yêu cầu về Tính mở rộng
NFR-4.1: Kiến trúc hệ thống phải cho phép mở rộng từng thành phần (service) một cách độc lập khi số lượng người dùng và dữ liệu tăng lên.
5. Yêu cầu về Giao diện
5.1. Giao diện Người dùng (UI)
IF-1.1: Phân hệ website phải được xây dựng theo kiến trúc MVC.
IF-1.2: Ngôn ngữ backend cho phân hệ website là PHP hoặc Python, có thể sử dụng framework.
5.2. Giao diện Hệ thống (API)
IF-2.1: Giao tiếp đồng bộ giữa các service sẽ được thực hiện thông qua REST API.
IF-2.2: Giao tiếp bất đồng bộ (ví dụ: gửi thông báo, xử lý tác vụ nền) sẽ sử dụng RabbitMQ.
IF-2.3: Hệ thống phải có giao diện để kết nối và trao đổi dữ liệu với Cổng Giám định BHYT của cơ quan Bảo hiểm xã hội.


Mô tả chi tiết các thành phần
Actors (Tác nhân)
Bệnh nhân (Patient)

Actor chính của hệ thống
Tham gia vào toàn bộ quy trình từ đăng ký đến lãnh thuốc
Nhân viên tiếp đón (Reception Staff)

Thực hiện đăng ký khám bệnh
Kiểm tra thẻ BHYT thông qua hệ thống BHXH
Quản lý thông tin bệnh nhân
Bác sĩ (Doctor)

Thực hiện khám lâm sàng
Chỉ định xét nghiệm khi cần thiết
Tạo đơn thuốc sau khi có kết quả
Kỹ thuật viên (Technician)

Thực hiện các xét nghiệm cận lâm sàng
Cập nhật kết quả xét nghiệm
Dược sĩ (Pharmacist)

Soạn thuốc theo đơn
Cấp phát thuốc cho bệnh nhân
Hệ thống BHXH (BHXH System)

Actor hệ thống bên ngoài
Cung cấp dịch vụ xác thực thẻ BHYT
Use Cases chính
1. Đăng ký khám bệnh (Register Examination)

Nhân viên tiếp đón tạo lịch khám cho bệnh nhân
Bao gồm việc tạo mới hoặc tra cứu thông tin bệnh nhân
2. Kiểm tra thẻ BHYT (Check Health Insurance Card)

Xác thực tính hợp lệ của thẻ BHYT
Kết nối với hệ thống BHXH để kiểm tra
3. Khám lâm sàng (Clinical Examination)

Bác sĩ thực hiện khám bệnh
Đánh giá tình trạng sức khỏe bệnh nhân
4. Chỉ định xét nghiệm (Order Tests)

Bác sĩ yêu cầu thực hiện các xét nghiệm bổ sung
Tạo phiếu chỉ định CLS
5. Thực hiện xét nghiệm (Perform Laboratory Tests)

Kỹ thuật viên thực hiện các xét nghiệm đã được chỉ định
Cập nhật kết quả vào hệ thống
6. Tạo đơn thuốc (Create Prescription)

Bác sĩ kê đơn thuốc dựa trên chẩn đoán
Liên kết với thông tin bệnh nhân và lượt khám
7. Lãnh thuốc (Dispense Medicine)

Dược sĩ soạn và cấp phát thuốc
Cập nhật trạng thái đơn thuốc
8. Quản lý hồ sơ bệnh nhân (Manage Patient Records)

Lưu trữ và cập nhật thông tin bệnh nhân
Theo dõi lịch sử khám chữa bệnh
Các mối quan hệ trong diagram
Association (Liên kết)

Kết nối giữa các actor và use case mà họ tham gia
Thể hiện ai có thể thực hiện chức năng nào
Include (Bao gồm)

"Đăng ký khám bệnh" include "Kiểm tra thẻ BHYT"
"Khám lâm sàng" include "Quản lý hồ sơ bệnh nhân"
Extend (Mở rộng)

"Chỉ định xét nghiệm" extend "Khám lâm sàng" (chỉ khi cần thiết)
"Thực hiện xét nghiệm" extend "Chỉ định xét nghiệm"
Luồng quy trình chính
Giai đoạn 1: Tiếp đón & Đăng ký

Bệnh nhân đến tiếp đón
Nhân viên đăng ký khám bệnh
Kiểm tra thẻ BHYT qua hệ thống BHXH
Tạo phiếu khám


Giai đoạn 2: Khám lâm sàng

Bác sĩ khám bệnh nhân
Tra cứu hồ sơ bệnh án
Quyết định có cần xét nghiệm hay không


Giai đoạn 3: Xét nghiệm (nếu cần)

Bác sĩ chỉ định xét nghiệm
Kỹ thuật viên thực hiện xét nghiệm
Cập nhật kết quả


Giai đoạn 4: Kết luận & Kê đơn

Bác sĩ xem kết quả (nếu có)
Đưa ra chẩn đoán cuối cùng
Tạo đơn thuốc
Giai đoạn 5: Lãnh thuốc

Bệnh nhân đến nhà thuốc
Dược sĩ soạn thuốc theo đơn
Cấp phát thuốc cho bệnh nhân


Nghiệp vụ thực tế: Quy trình Khám bệnh Ngoại trú có BHYT

Bối cảnh: Một bệnh nhân (đã có hoặc chưa có hồ sơ tại bệnh viện) đến khám bệnh và muốn sử dụng thẻ BHYT để được chi trả chi phí.

Giai đoạn 1: Tiếp đón & Đăng ký Khám

Đây là điểm bắt đầu của luồng đi.

Hành động thực tế:

Bệnh nhân đến quầy tiếp đón, lấy số thứ tự.

Khi đến lượt, bệnh nhân trình thẻ BHYT và giấy tờ tùy thân (CCCD) cho nhân viên tiếp đón.

Nhân viên tiếp đón sử dụng phần mềm của bệnh viện (kết nối với cổng thông tin của BHXH) để kiểm tra thông tin thẻ BHYT (tính hợp lệ, nơi đăng ký ban đầu).

Nếu hợp lệ, nhân viên sẽ hỏi bệnh nhân về chuyên khoa muốn khám (ví dụ: Tim mạch, Tiêu hóa, Tai-mũi-họng).

Nhân viên đăng ký một lượt khám cho bệnh nhân trên hệ thống, in ra một phiếu khám bệnh có ghi số thứ tự, phòng khám và tên bác sĩ.

Bệnh nhân nhận phiếu và di chuyển đến phòng khám được chỉ định.

Ánh xạ vào Hệ thống Microservices của bạn:

Patient Service:

Nếu là bệnh nhân mới, nhân viên sẽ thực hiện chức năng

Đăng ký thông tin bệnh nhân mới.

Nếu là bệnh nhân cũ, nhân viên sẽ

tra cứu thông tin bệnh nhânđể tái khám.

Appointment Service:

Nhân viên tạo một "lịch khám" trong ngày cho bệnh nhân, tương ứng với chức năng

Đặt lịch khám. Hệ thống cần tự động phân bổ bác sĩ phù hợp.

Giai đoạn 2: Khám lâm sàng tại Phòng khám

Đây là nơi tương tác chính giữa bác sĩ và bệnh nhân.

Hành động thực tế:

Bệnh nhân chờ đến số thứ tự của mình được gọi trên bảng điện tử hoặc do điều dưỡng gọi.

Vào phòng khám, bác sĩ tiếp nhận phiếu khám và tra cứu hồ sơ bệnh án điện tử của bệnh nhân.

Bác sĩ hỏi bệnh, khám lâm sàng (đo huyết áp, nghe tim phổi...).

Điểm quyết định:

Trường hợp 1 (Bệnh đơn giản): Bác sĩ chẩn đoán và kê đơn thuốc ngay.

Trường hợp 2 (Cần xét nghiệm): Bác sĩ chỉ định bệnh nhân thực hiện các xét nghiệm cận lâm sàng (gọi tắt là CLS) như xét nghiệm máu, siêu âm, X-quang... Bác sĩ sẽ in ra phiếu chỉ định CLS.

Ánh xạ vào Hệ thống Microservices của bạn:

Patient Service: Bác sĩ sử dụng chức năng tra cứu thông tin bệnh nhân (hồ sơ bệnh án, lịch sử khám chữa bệnh).

Appointment Service: Hệ thống của bác sĩ hiển thị danh sách bệnh nhân đang chờ khám.

(Gợi ý mở rộng): Việc chỉ định CLS có thể là một sự kiện (event) được gửi đi. Ví dụ, Appointment Service gửi một message tới một Testing Service (Dịch vụ Xét nghiệm) để tạo yêu cầu xét nghiệm cho bệnh nhân.

Giai đoạn 3: Thực hiện Cận lâm sàng (CLS)

Giai đoạn này không áp dụng cho mọi bệnh nhân.

Hành động thực tế:

Bệnh nhân cầm phiếu chỉ định CLS đến các phòng xét nghiệm/chẩn đoán hình ảnh tương ứng.

Bệnh nhân nộp phiếu, đóng phí (nếu có phần đồng chi trả) và chờ đến lượt.

Kỹ thuật viên thực hiện xét nghiệm/chụp chiếu.

Kết quả CLS có thể được trả bằng bản cứng cho bệnh nhân hoặc được đẩy tự động lên hệ thống phần mềm của bệnh viện và liên kết với hồ sơ của bệnh nhân.

Ánh xạ vào Hệ thống Microservices của bạn:

Đây là một nghiệp vụ quan trọng. Kết quả từ Testing Service (gợi ý ở trên) cần được cập nhật và liên kết lại với Patient Service để bác sĩ có thể xem được.

Giao tiếp ở đây có thể là bất đồng bộ. Khi có kết quả, Testing Service sẽ gửi một thông điệp qua RabbitMQ để Notification Service thông báo cho bệnh nhân (nếu hệ thống hỗ trợ) và cập nhật trạng thái cho Appointment Service.

Giai đoạn 4: Quay lại phòng khám & Nhận kết quả cuối cùng

Hành động thực tế:

Bệnh nhân mang kết quả CLS (nếu là bản cứng) quay lại phòng khám ban đầu.

Bác sĩ xem kết quả (trên giấy hoặc trên máy tính) cùng với thông tin khám lâm sàng để đưa ra chẩn đoán cuối cùng.

Bác sĩ tiến hành kê đơn thuốc.

Ánh xạ vào Hệ thống Microservices của bạn:

Prescription Service: Bác sĩ sử dụng chức năng Tạo đơn thuốc cho bệnh nhân sau khi khám. Đơn thuốc này phải được liên kết với ID bệnh nhân và ID của lượt khám.

Giai đoạn 5: Lãnh thuốc

Đây là bước cuối cùng trong quy trình.

Hành động thực tế:

Bệnh nhân cầm đơn thuốc (đã được bác sĩ ký và đóng dấu hoặc là đơn thuốc điện tử) đến nhà thuốc của bệnh viện.

Dược sĩ kiểm tra đơn thuốc, soạn thuốc theo đơn.

Bệnh nhân ký nhận thuốc.

Thông tin cấp phát thuốc được cập nhật trên hệ thống để BHYT quyết toán.

Ánh xạ vào Hệ thống Microservices của bạn:

Prescription Service: Dược sĩ sẽ truy cập và Cập nhật tình trạng đơn thuốc (đã lấy, chưa lấy).