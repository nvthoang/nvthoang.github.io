# Hướng dẫn vận hành website — Hoang Nguyen Research Group

## 1. Xem website trước

Giải nén source, vào thư mục `dist`, mở `index.html` bằng trình duyệt. Các trang và bộ lọc chạy từ file tĩnh. Để xem chính xác hơn, cài Python 3.11+ và mở terminal tại thư mục chứa `README.md`:

```bash
python -m http.server 8000 --directory dist
```

Trên Windows có thể dùng `py` thay cho `python`. Mở `http://localhost:8000`. Nút VI cần website đã online, nên trong bản local sẽ hiện thông báo thay vì dịch.

## 2. Đưa source lên GitHub

1. Đăng nhập tài khoản `nvthoang`.
2. Tạo một repository mới, ví dụ **research-group**, chọn Public nếu dùng GitHub Free. Nếu anh đã có repo cho website thì dùng repo đó và bảo toàn nội dung hiện có.
3. Đưa **toàn bộ nội dung bên trong thư mục source** vào gốc repository, không upload nguyên file ZIP. Tại gốc phải thấy `README.md`, `content`, `assets`, `scripts`, `templates`, `dist` và **`.github/workflows/pages.yml`**.
4. Vào **Settings → Pages → Build and deployment → Source → GitHub Actions**.
5. Vào **Actions → Build and deploy academic website → Run workflow**, chọn nhánh `main`. Các lần sau chỉ cần commit/push thay đổi vào `main`; GitHub sẽ tự dựng lại và deploy.
6. Đợi workflow thành công rồi mở URL do GitHub Pages trả về. Nếu build đỏ, mở bước lỗi; lỗi BibTeX sẽ nêu dòng hoặc citation key cần sửa.

Nếu dùng Git CLI với **repository mới trống**, có thể dùng các lệnh dưới đây từ thư mục source. Ví dụ này giả định anh vừa tạo repo `research-group`; thay tên nếu khác. Không chạy để ghi đè một repo hiện có.

```bash
git init -b main
git add .
git commit -m "Add academic research website"
git remote add origin https://github.com/nvthoang/research-group.git
git push -u origin main
```

Không có token/password nào trong source. GitHub có thể yêu cầu anh đăng nhập qua phương thức Git đang dùng. Nếu repo dùng nhánh khác `main`, sửa các điều kiện nhánh trong `.github/workflows/pages.yml` cho khớp.

## 3. Kết nối www.nvthoang.com

**Trước hết thêm domain trong GitHub**, sau đó mới chỉnh DNS. Nếu domain đang phục vụ website cũ, các thay đổi DNS sẽ chuyển lưu lượng sang website mới: chỉ đổi khi anh đã xem và sẵn sàng dùng bản mới.

1. Khuyến nghị xác minh domain trong phần Pages của tài khoản GitHub bằng bản ghi TXT mà GitHub cung cấp.
2. Trong **repository → Settings → Pages → Custom domain**, nhập `www.nvthoang.com`, lưu lại.
3. Ở nhà cung cấp domain/DNS, cấu hình:

| Loại | Host | Giá trị |
| --- | --- | --- |
| CNAME | `www` | `nvthoang.github.io` |

Không thêm tên repository vào giá trị CNAME. Không thay đổi các bản ghi email MX/TXT hiện có. Không tạo hai CNAME cho cùng host `www`.

Nếu muốn cả `nvthoang.com` chuyển về `www.nvthoang.com`, dùng cấu hình apex được GitHub hướng dẫn. Với phương án A record:

| Loại | Host | Giá trị |
| --- | --- | --- |
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |

Chờ GitHub kiểm tra DNS và cấp chứng chỉ, sau đó bật **Enforce HTTPS**. GitHub lưu ý DNS và HTTPS có thể cần đến 24 giờ. Tham khảo hướng dẫn chính thức nếu nhà cung cấp có cấu hình riêng:

https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

`dist/CNAME` đã chuẩn bị sẵn, nhưng **với GitHub Actions anh vẫn phải nhập domain trong Settings → Pages**. Nếu đổi domain, sửa `site_url` trong `content/site.json` và build lại để cập nhật canonical/sitemap/link dịch.

## 4. Kích hoạt form nhận thư

Form đã trỏ tới **hoang.nguyen@weltec.ac.nz** thông qua FormSubmit, không cần API key.

1. Khi website đã chạy HTTPS, tự điền một liên hệ thử trên trang Contact.
2. Form chuyển sang FormSubmit; hoàn thành bước kiểm tra spam nếu có.
3. Mở hộp thư `hoang.nguyen@weltec.ac.nz`, tìm email kích hoạt FormSubmit, kiểm tra cả Junk/Spam và nhấn link xác nhận.
4. Quay lại website, gửi **một liên hệ thử mới sau khi kích hoạt**. Kiểm tra thư thực sự đến nơi và Reply-To trỏ về email người gửi.
5. Nếu không nhận được, kiểm tra Junk/Spam hoặc bộ lọc thư cơ quan; có thể cần quản trị email hỗ trợ. Trong thời gian đó khách vẫn có link email trực tiếp.

Không giả định lần gửi dùng để kích hoạt đã được chuyển đầy đủ. Form dùng POST thông thường, giữ màn hình CAPTCHA/lỗi của nhà cung cấp và không hiển thị thông báo giả “đã giao thư”. Trong lần xây dựng này chưa gửi thử hoặc kích hoạt dịch vụ thay anh.

Sau khi xác nhận email, FormSubmit có thể cung cấp endpoint dạng mã để thay địa chỉ email trong form. Nếu muốn, sửa `form_endpoint` trong `content/site.json` rồi commit. Email trực tiếp vẫn đang hiển thị công khai trên Contact theo cấu hình của anh.

## 5. Nút VI hoạt động như thế nào

- Anh chỉ viết và cập nhật nội dung **tiếng Anh**.
- Khi nhấn VI, trang đang xem được mở qua Google Translate với ngôn ngữ đích **tiếng Việt**.
- Bản dịch có thể nằm tại địa chỉ của Google và hiển thị thanh công cụ dịch. EN quay về trang gốc tiếng Anh; thanh dịch của Google cũng có tùy chọn xem bản gốc.
- Giải pháp này không cần API trả phí, không yêu cầu anh viết hai bản, và không nhúng API key vào source.
- **Không có cache bản dịch do website quản lý**, không có bản tiếng Việt lưu trong repository; Google quyết định khi nào lấy lại nội dung. Sau khi cập nhật website có thể cần tải lại hoặc chờ dịch vụ cập nhật bản lấy về.
- Google không truy cập được `localhost`/file trên máy. Bản xem local sẽ nhắc cần deploy trước. Không coi đó là lỗi thiếu bản tiếng Việt.
- Tính sẵn có tùy vùng/trình duyệt/dịch vụ. Thuật ngữ học thuật có thể dịch sai; bản gốc tiếng Anh là bản tham chiếu. Tên bài báo và trích dẫn được đánh dấu giữ nguyên tiếng Anh.

Đây là phương án miễn phí mở bản dịch qua Google, **không phải API dịch native trong domain**. Nếu sau này anh cần chỉnh từng bản dịch, giữ domain khi chuyển ngôn ngữ hoặc lưu cache theo phiên bản nội dung, cần bổ sung quy trình dịch khác.

## 6. Cập nhật publications bằng BibTeX

1. Vào Google Scholar, chọn các công trình **đã xuất bản** cần đưa lên.
2. Export thành BibTeX.
3. Thay hoặc bổ sung `content/publications.bib` bằng dữ liệu đó. Chỉ dùng citation key duy nhất.
4. Nếu muốn có bộ lọc chủ đề, bổ sung trường như:

```bibtex
keywords={Bioinformatics, Deep Learning},
status={published},
```

5. Sửa `featured_publications` trong `content/site.json` để chọn các citation key hiện có làm highlights. Nếu thay citation key của bài đã liên kết trong news, sửa trường `publication` trong file news tương ứng.
6. Commit lên GitHub. Workflow sẽ tự kiểm tra và build lại trang Publications.

Hiện có **32 công trình trong giai đoạn 2016–2026**: toàn bộ 26 bài tạp chí, 5 bài kỷ yếu hội nghị và 1 chương sách trong CV tháng 10/2026. Poster JACC 2020 được loại theo yêu cầu của anh. Chưa thể đối chiếu đầy đủ với hồ sơ Scholar hiện tại vì link được cung cấp không đọc được toàn bộ; xem `PUBLICATION_SOURCES.md`. Năm và nội dung ba tin ban đầu dựa trên bài đã xuất bản; không tự tạo ngày chấp nhận bài hoặc kết quả thực nghiệm.

Script loại entry không thuộc dạng xuất bản hỗ trợ, entry có status chưa xuất bản, hoặc venue arXiv/bioRxiv/medRxiv. Tuy vậy, **Google Scholar không đảm bảo metadata luôn phân biệt được preprint**, nên anh cần duyệt dữ liệu export. Nguồn không có status ở dạng article/inproceedings sẽ được xem là đã được anh duyệt. Không đưa manuscript chưa công bố vào source repository công khai.

## 7. News, projects, thành viên và tài nguyên

| Cần sửa | Vị trí |
| --- | --- |
| Tiểu sử, liên kết, địa chỉ cơ quan | `content/site.json` |
| Project | Mảng `projects` trong `content/site.json` |
| Researcher / RA | Mảng `people` trong `content/site.json` |
| Teaching/Resources | Mảng `resources` trong `content/site.json` |
| News | File `.md` mới trong `content/news` |
| Bài nổi bật trang chủ | `featured_publications` và `featured: true` trong news |
| Màu sắc, font, bố cục | `assets/style.css` |

Ví dụ news mới:

```markdown
---
title: A short English update
date: 2026-10-27
category: Publication
featured: true
published: true
---
Write a short, factual update in English.

[Read more](https://example.org)
```

Ví dụ một RA trong mảng `people`:

```json
{"name":"Full name", "role":"Research Assistant", "bio":"Short approved public biography.", "url":"", "image":"", "published":true}
```

Có ba vai trò thành viên: `Senior Researcher`, `Researcher` và `Research Assistant`; anh được hiển thị riêng là group lead. Bảy hồ sơ do anh cung cấp đã được thêm bằng tiếng Anh. Không tự lấy danh sách supervisee từ CV để biến thành thành viên nhóm. Với project, thay nội dung placeholder và đặt `placeholder` thành `false`. `published: false` ẩn khỏi website sinh ra, **không làm nội dung bí mật trong repo**.

Schema đầy đủ và ví dụ: `content/README.md`. Tin viết Markdown hỗ trợ đoạn văn, heading cấp 2/3, bullet, bold, italic và link. Không hỗ trợ HTML tùy ý. Resource dùng file trong `assets/` hoặc URL HTTPS. Có thể thêm CV PDF đã rà soát thông tin công khai rồi điền đường dẫn `cv_file`; CV không tự được tạo/cập nhật từ Scholar.

## 8. Build và kiểm tra tại máy

Chạy từ thư mục chứa source:

```bash
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/check.py
```

`build.py` chỉ ghi vào `dist`, giữ nguồn trong `content`. Sửa nội dung trong source thay vì chỉnh trực tiếp HTML trong `dist`, vì lần build sau sẽ ghi lại thư mục đó. Bộ kiểm tra xác nhận link local, anchor, ảnh và cấu trúc HTML cơ bản; nó không kiểm tra gửi mail thật, Google Translate hay xác thực mọi DOI.

Không cần cài pip package. Site chạy được cả với JavaScript tắt (nội dung và form HTML vẫn hiện), nhưng bộ lọc, copy citation và menu mobile thu gọn dùng JavaScript. Nếu tắt JavaScript, menu hiện đầy đủ để vẫn điều hướng được.
