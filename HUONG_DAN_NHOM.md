# GlucoGuide – Hướng dẫn nhanh cho nhóm

Tài liệu nội bộ giúp các thành viên hiểu cách chạy ứng dụng, nắm quy trình xử lý dữ liệu và xây dựng mô hình, chuẩn bị thuyết trình và thực hiện demo.

---

## 1. Chạy ứng dụng

### 1.1. Môi trường

- Python **3.13.9**
- scikit-learn **1.7.1**
- Các thư viện được khai báo trong `requirements.txt`

### 1.2. Cài đặt và chạy app

Mở Terminal tại thư mục gốc `project`, tạo môi trường ảo:

```bash
python -m venv .venv
```

Kích hoạt môi trường:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Cài dependencies và chạy ứng dụng:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**Lưu ý:**

- Model đã được train và lưu sẵn. Không cần chạy `train.py` khi chỉ muốn sử dụng app.
- Chỉ chạy lại `train.py` khi cần huấn luyện hoặc cập nhật kết quả.
- Các lệnh trên được nhập trong Terminal, không nhập vào file Python.
- Nên sử dụng đúng phiên bản Python và scikit-learn nêu trên để đồng nhất môi trường.

---

## 2. Những nội dung cần hiểu khi thuyết trình

### 2.1. Problem and Target

**Mục tiêu:** Xây dựng ứng dụng hỗ trợ sàng lọc sơ bộ nguy cơ diabetes/prediabetes thông qua các chỉ số sức khỏe cơ bản.

Biến mục tiêu: `Diabetes_binary`

| Nhãn | Ý nghĩa |
|---|---|
| 0 | Không tự khai mắc diabetes/prediabetes |
| 1 | Tự khai mắc diabetes hoặc prediabetes |

Đây là nhãn dựa trên khảo sát tự khai, không phải kết quả xét nghiệm lâm sàng và cũng không phải nhãn dự báo bệnh phát sinh trong tương lai.

Khi thuyết trình, nên nói:

> GlucoGuide estimates the likelihood of a positive diabetes/prediabetes survey label based on the available health indicators.

Không nói rằng app chẩn đoán người dùng mắc diabetes.

### 2.2. Dataset and Data Cleaning

Dataset: Diabetes Health Indicators, có nguồn gốc từ khảo sát BRFSS 2015 của CDC.

- Tổng số quan sát: **253,680**.
- Tổng số cột: 22, gồm 21 biến đầu vào và 1 biến mục tiêu.
- Tỷ lệ nhãn dương tính ban đầu: khoảng **13.93%**.
- Không có missing values theo báo cáo kiểm tra dữ liệu.
- Có 24,206 dòng trùng hoàn toàn được phát hiện trong quá trình audit.

**Vì sao không tự động xóa dòng trùng?**

Dataset không có mã định danh người tham gia để xác định các dòng giống nhau có phải là cùng một cá nhân hay không. Những người khác nhau có thể có cùng câu trả lời khảo sát.

Nhóm giữ lại dữ liệu gốc và sử dụng cách chia tập theo nhóm hồ sơ: các hồ sơ có cùng 21 biến đầu vào được giữ trong cùng một tập train, validation hoặc test để hạn chế leakage giữa các tập.

**Kích thước các tập dữ liệu:**

| Tập | Số quan sát |
|---|---:|
| Train | 151,933 |
| Validation | 50,684 |
| Test | 51,063 |

Tỷ lệ chia xấp xỉ 60/20/20, có phân tầng và nhóm các hồ sơ có cùng bộ biến đầu vào.

### 2.3. Feature Selection – Chọn biến

Dataset ban đầu có 21 biến đầu vào. Nhóm so sánh mô hình sử dụng toàn bộ biến với mô hình sử dụng bộ biến rút gọn.

**Bộ 5 features cuối cùng:**

| Feature | Ý nghĩa |
|---|---|
| `Age` | Nhóm tuổi |
| `BMI` | Chỉ số khối cơ thể |
| `HighBP` | Tiền sử huyết áp cao |
| `HighChol` | Tiền sử cholesterol cao |
| `GenHlth` | Tự đánh giá tình trạng sức khỏe tổng quát |

Bộ biến rút gọn được lựa chọn nhằm giảm số thông tin người dùng phải cung cấp, đồng thời duy trì khả năng dự đoán ở mức chấp nhận được.

Kết quả validation:

- Full features – Gradient Boosting: ROC-AUC **0.8273**.
- Short features – Gradient Boosting: ROC-AUC **0.8197**.
- Chênh lệch AUC: khoảng **0.00765**, thấp hơn mức chênh lệch tối đa 0.010 trong quy tắc lựa chọn của nhóm.

**Lưu ý:** BMI là một feature của mô hình. Nếu giao diện yêu cầu chiều cao và cân nặng để tính BMI thì số trường nhập trên app có thể nhiều hơn số features của model.

### 2.4. Model Selection – Chọn mô hình

Nhóm đã so sánh ba thuật toán:

- Logistic Regression (LR)
- Random Forest (RF)
- Gradient Boosting (GB)

Các mô hình được đánh giá trên validation set, không lựa chọn dựa trên test set.

**Mô hình cuối cùng: Gradient Boosting – bộ 5 features.**

Lý do:

- Short Gradient Boosting đạt validation ROC-AUC khoảng 0.8197.
- Kết quả nhỉnh hơn một chút so với Short Logistic Regression (0.8186).
- Brier score của Short Gradient Boosting cũng thấp hơn một chút.
- Chênh lệch giữa hai mô hình nhỏ, nhưng Gradient Boosting là lựa chọn cuối cùng theo quyết định của nhóm.

Baseline Logistic Regression chỉ sử dụng Age và BMI có validation ROC-AUC khoảng 0.7506.

**Khi thuyết trình:** Phải phân biệt model được đem ra so sánh với model cuối cùng được lưu và sử dụng trong app.

Thông tin xác nhận model hiện tại trong `model_meta.json`:

- `algorithm`: Gradient Boosting
- `selected_candidate`: short | Gradient Boosting

### 2.5. Class Imbalance – Mất cân bằng dữ liệu

Tỷ lệ nhãn dương tính trong dataset chỉ khoảng 13.93%, nên dữ liệu bị mất cân bằng.

Nhóm:
- Giữ nguyên phân phối lớp ban đầu.
- Không oversampling hoặc chuyển dữ liệu thành tỷ lệ 50/50.
- Không sử dụng class weights trong cấu hình hiện tại.
- Đánh giá bằng ROC-AUC, PR-AUC, precision, recall, F1-score và Brier score thay vì chỉ dựa vào accuracy.

**Ý nghĩa các chỉ số:**

- Precision: Trong các trường hợp được dự đoán dương tính, có bao nhiêu trường hợp thực sự mang nhãn dương tính.
- Recall: Trong các trường hợp thực sự mang nhãn dương tính, mô hình nhận diện được bao nhiêu.
- PR-AUC: Đánh giá sự đánh đổi giữa precision và recall, hữu ích khi dữ liệu mất cân bằng.
- Brier score: Đánh giá sai số của xác suất dự đoán; giá trị thấp hơn thường tốt hơn.

### 2.6. Threshold – Ngưỡng phân loại

Threshold mặc định hiện tại:

<badge color="success">15.83%</badge>

Ngưỡng được lựa chọn trên validation set theo giả định chi phí:

- False Positive (FP) = 1
- False Negative (FN) = 5

**Vì sao FN có chi phí cao hơn FP?**

Trong bối cảnh sàng lọc, bỏ sót một trường hợp có nhãn dương tính tiềm năng có thể đáng quan tâm hơn việc tạo ra một cảnh báo dương tính giả. Vì vậy, nhóm giả định FN có chi phí cao hơn FP.

Đây là đơn vị chi phí tương đối để minh họa sự đánh đổi, không phải tiền hoặc chi phí y tế thực tế.

**Điểm cần nhớ:**

- Xác suất dự đoán là đầu ra của mô hình.
- Threshold là ngưỡng dùng để chuyển xác suất thành nhãn dự đoán.
- Thay đổi threshold không làm thay đổi xác suất dự đoán.
- Threshold thấp thường tăng recall nhưng có thể làm tăng false positives.
- Threshold cao thường giảm false positives nhưng có thể làm tăng số trường hợp bị bỏ sót.

### 2.7. Test Results – Kết quả đánh giá

Kết quả trên test set của model hiện tại:

| Metric | Test result |
|---|---:|
| ROC-AUC | 0.8184 |
| PR-AUC (Average Precision) | 0.4128 |
| Brier score | 0.0980 |
| Precision | 31.5% |
| Recall | 73.6% |
| F1-score | 44.1% |

Test set có 51,063 quan sát, trong đó 7,065 quan sát mang nhãn dương tính.

**Confusion matrix:**

| | Predicted 0 | Predicted 1 |
|---|---:|---:|
| Actual 0 | 32,676 | 11,322 |
| Actual 1 | 1,866 | 5,199 |

Cách giải thích:

- ROC-AUC 0.8184 cho thấy mô hình có khả năng phân biệt hai nhóm ở mức tương đối tốt trên test set.
- Recall 73.6% nghĩa là mô hình nhận diện được khoảng 73.6% trường hợp mang nhãn dương tính trong test set.
- Precision 31.5% nghĩa là trong các trường hợp được dự đoán dương tính, khoảng 31.5% thực sự mang nhãn dương tính.
- Có 11,322 false positives và 1,866 false negatives ở threshold hiện tại.

**Hạn chế cần nhấn mạnh:** Precision tương đối thấp, nghĩa là có nhiều cảnh báo dương tính giả. Không nên chỉ nhấn mạnh ROC-AUC hoặc recall mà bỏ qua điểm này.

### 2.8. Kiểm tra kết quả sau khi loại dòng trùng

Ngoài kết quả test trên dữ liệu gốc, metadata còn ghi nhận một phép kiểm tra phụ sau khi loại các dòng trùng:

| Metric | Test gốc | Test sau deduplication |
|---|---:|---:|
| ROC-AUC | 0.8184 | 0.8018 |
| PR-AUC | 0.4128 | 0.4156 |
| Precision | 31.5% | 31.9% |
| Recall | 73.6% | 73.7% |
| F1-score | 44.1% | 44.5% |

Đây là phân tích độ nhạy để quan sát ảnh hưởng của các dòng trùng đến kết quả đánh giá. Không nhầm kết quả này với test result chính được báo cáo trong phần trước.

### 2.9. Model Interpretation – Giải thích mô hình

Model cuối là Gradient Boosting, không phải Logistic Regression.

Metadata ghi nhận phương pháp giải thích sử dụng **Exact Shapley values** trên thang xác suất.

- Giá trị Shapley cho biết từng feature đóng góp như thế nào vào xác suất dự đoán của một hồ sơ.
- Các đóng góp được so sánh với mức xác suất trung bình của một tập background gồm 1,000 hồ sơ từ training set.
- Tổng các đóng góp bằng chênh lệch giữa xác suất dự đoán của hồ sơ và mức xác suất nền.

**Lưu ý:** Đây là cách giải thích đóng góp của feature vào dự đoán, không chứng minh feature đó là nguyên nhân gây bệnh.

### 2.10. Fairness – Kiểm tra khác biệt giữa các nhóm

Nhóm xem xét hiệu suất mô hình theo các nhóm dân số:

- Age
- Sex
- Income
- Education

Các chỉ số cần chú ý:

- Recall
- False Positive Rate (FPR)
- Số lượng quan sát trong từng nhóm

Mục tiêu là xem mô hình có hoạt động khác nhau giữa các nhóm hay không.

**Lưu ý:** Phân tích subgroup là bước kiểm tra mô tả. Không đủ cơ sở để tuyên bố mô hình hoàn toàn công bằng hoặc không có bias.

### 2.11. Limitations – Hạn chế

Các hạn chế chính:

- Dataset dựa trên khảo sát tại Mỹ năm 2015.
- Thông tin chủ yếu là tự khai nên có thể có sai lệch trong báo cáo.
- Một số người có thể chưa biết mình mắc bệnh hoặc chưa được chẩn đoán.
- Dataset không đại diện trực tiếp cho dân số Việt Nam.
- Bộ 5 features giúp giảm số thông tin cần nhập nhưng không bao quát toàn bộ yếu tố sức khỏe liên quan.
- Mô hình chưa được kiểm định lâm sàng hoặc kiểm định trên dữ liệu người Việt Nam.

Vì vậy, GlucoGuide chỉ có mục đích hỗ trợ nhận thức và sàng lọc sơ bộ, không thay thế xét nghiệm, chẩn đoán hoặc tư vấn y tế.

---

## 3. Phân chia công việc gợi ý

| Part | Files / Tasks |
|---|---|
| Data and ML | `train.py`, `utils/data_loader.py`, data audit, feature selection, model selection, threshold selection |
| UI/UX | `app.py`, `pages/`, câu hỏi đầu vào, tính BMI, giải thích kết quả |
| Evaluation and Deployment | `utils/threshold.py`, fairness reports, README, GitHub, Streamlit Cloud |

Dù có phân chia nhiệm vụ, tất cả thành viên cần hiểu toàn bộ quy trình:

**Data → Cleaning → Feature Selection → Model Training → Threshold Selection → Evaluation → Streamlit App**

Các tài liệu cần đọc:

- `README.md`: Giới thiệu project và hướng dẫn cài đặt/chạy app.
- `DECISION_LOG.md`: Ghi lại các quyết định quan trọng của nhóm.
- `AI_USE_APPENDIX.md`: Rà soát và hoàn thiện phần khai báo sử dụng AI trước khi nộp.

---

## 4. Demo ứng dụng

### Demo flow

1. **Home:** Giới thiệu mục đích và cách sử dụng GlucoGuide.
2. **BMI Calculator:** Nhập chiều cao và cân nặng để tính BMI.
3. **Start Assessment:** Trả lời các câu hỏi sức khỏe.
4. **My Results:** Xem kết quả dự đoán và các yếu tố đóng góp.
5. **Threshold Simulator:** Thay đổi giả định chi phí và quan sát threshold, FP và FN.
6. **About & Model:** Xem thông tin dataset, mô hình, ROC curve, confusion matrix và fairness.

### Những điểm cần nhấn mạnh

- App ước lượng khả năng mang nhãn khảo sát dương tính, không chẩn đoán bệnh.
- Model cuối là Gradient Boosting sử dụng 5 features.
- Threshold Simulator minh họa sự đánh đổi giữa bỏ sót và cảnh báo dương tính giả.
- Kết quả cần được hiểu trong bối cảnh dữ liệu và những hạn chế của mô hình.

**Cách diễn đạt nên dùng:**

> GlucoGuide estimates the likelihood of a positive diabetes/prediabetes survey label and supports preliminary health risk awareness.

**Không nên nói:**

> GlucoGuide determines whether a person has diabetes.

---

## 5. Final Checklist Before Submission

- [ ] Kiểm tra Python 3.13.9 và scikit-learn 1.7.1.
- [ ] Kiểm tra `requirements.txt`.
- [ ] Xác nhận model cuối trong `model_meta.json` là Gradient Boosting.
- [ ] Xác nhận 5 features được sử dụng trong model.
- [ ] Xác nhận threshold mặc định khoảng 15.83%.
- [ ] Kiểm tra giả định chi phí FP = 1, FN = 5.
- [ ] Cập nhật metrics theo kết quả train mới nhất.
- [ ] Kiểm tra `pipeline.joblib` có thể load trong Streamlit.
- [ ] Kiểm tra các báo cáo ROC, PR và fairness.
- [ ] Chạy thử toàn bộ luồng demo.
- [ ] Rà soát README, DECISION_LOG và AI_USE_APPENDIX.

**Final reminder:** GlucoGuide is an educational screening decision-support application. It is not a substitute for professional medical advice, clinical testing, diagnosis, or treatment.