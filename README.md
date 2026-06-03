# Omron FINS Tester

Omron FINS Tester, endüstriyel otomasyon mühendisleri için geliştirilmiş profesyonel ve arayüz (GUI) tabanlı bir Python uygulamasıdır. Omron PLC'leri üzerinde FINS UDP ve FINS TCP protokollerini kullanarak değişken okuma ve yazma işlemlerini yapmak için tasarlanmıştır.

Python, PyQt6 ve `fins` kütüphanesi ile inşa edilen bu araç; PLC IDE'lerinin ağır ve yavaş arayüzlerine kıyasla PLC belleğinin hızlıca test edilmesi, hata ayıklanması (debugging) ve sürekli olarak izlenmesi (monitoring) için hafif ve son derece hızlı bir alternatif sunar.

## Özellikler

- 🔌 **FINS UDP ve TCP Desteği**: İsteğe bağlı seçilebilen UDP ve TCP protokolleri. Ağ yönlendirme (Destination Node/Net, Source Node/Net) ve FINS TCP Düğüm Anlaşması (Handshake) ile tam uyumlu, sağlam haberleşme altyapısı.
- 🎨 **Endüstriyel Karanlık Tema (Dark Mode)**: Sysmac Studio ve VS Code gibi profesyonel yazılımlardan ilham alan, gözü yormayan modern arayüz tasarımı.
- ⏱️ **Otomatik Okuma (Auto-Read)**: Özelleştirilebilir milisaniye bazlı periyotlarla birden fazla değişkenin durumunu canlı olarak izleme yeteneği.
- ⚡ **Hızlı Veri Düzenleme (Inline Editing)**: 
  - Bool/Bit değerlerini anında kontrol edebilmek için atanmış `[TRUE]` / `[FALSE]` hızlı yazma butonları.
  - Sayısal değerleri kutuya yazıp doğrudan `Enter` tuşuna basarak saniyesinde PLC'ye gönderme imkanı.
- 🛠️ **Kapsamlı Veri Tipi Desteği**: `BOOL`, `WORD`, `DWORD`, `INT`, `DINT`, `REAL`, `LREAL`, `UINT` ve `UDINT` formatlarının otomatik olarak çözümlenmesi (parse edilmesi).
- 🔢 **Özelleştirilebilir Veri Gösterimi**: Değerleri anlık olarak `Decimal`, `Onaltılık (Hex)` veya `İkili (Binary)` formatlarda görüntüleyebilme ve yazabilme özelliği.
- 🛡️ **Hata Toleransı**: PLC bağlantı düşmelerini, yönlendirme gecikmelerini (timeout) ve Omron'a özgü başarılı sayılan hata kodlarını (örneğin `00 40`) programı çökertmeden UI üzerinde düzgünce ele alabilen sağlam altyapı.

## Kurulum

Bu proje, bağımlılık (dependency) yönetimi için oldukça hızlı olan `uv` paket yöneticisini kullanmaktadır.

1. Bilgisayarınızda Python 3.8 veya daha güncel bir sürümün kurulu olduğundan emin olun.
2. Depoyu bilgisayarınıza kopyalayın:
   ```bash
   git clone https://github.com/kullanici-adiniz/omron-fins-tester.git
   cd omron-fins-tester
   ```
3. Uygulamayı `uv` aracılığıyla çalıştırın (kütüphaneleri otomatik olarak indirip kuracaktır):
   ```bash
   uv run python src\omron_fins_tester\main.py
   ```

## Kullanım

1. **Bağlantı Ayarları**: 
   - PLC'nizin IP adresini girin (Örn: `192.168.250.1`).
   - Haberleşme için kullanacağınız **Protokolü** (`UDP` veya `TCP`) seçin.
   - `Dest Node` kısmına PLC IP'sinin son hanesini, `Src Node` kısmına ise kendi bilgisayarınızın IP'sinin son hanesini girin (TCP için `0` bırakırsanız program bu değerleri PLC'den otomatik alır).
   - **Bağlan** butonuna tıklayın.
2. **Değişken Ekleme**:
   - İlgili Bellek Alanını (Memory Area) seçin (Örn: Data Memory için `D`, CIO için `C`, Work için `W`, Holding için `H`).
   - Adresi girin (Örn: Word okumak için `200`, Bit okumak için `300.0`).
   - Veri Tipini (Data Type) seçin.
   - **Değişken Ekle** butonuna tıklayın.
3. **İzleme ve Yazma**:
   - Anlık okuma için satırdaki **Oku** butonunu kullanabilir veya tabloyu canlı izlemek için **Otomatik Okuma** kutucuğunu işaretleyebilirsiniz.
   - Veri yazmak için "Değiştir" sütununa değeri girip **Enter** tuşuna basmanız yeterlidir. Bit değerlerini kontrol etmek için ise doğrudan `TRUE` veya `FALSE` butonlarına tıklayabilirsiniz.

## Mimari ve Kod Yapısı

- `src/omron_fins_tester/main.py`: Uygulamanın başlatıldığı ana dosya.
- `src/omron_fins_tester/gui/`: Tüm PyQt6 arayüz (UI) kodlarını içerir (`app.py`, `connection.py`, `variables.py`).
- `src/omron_fins_tester/gui/style.qss`: Uygulamanın karanlık temasını yöneten CSS dosyası.
- `src/omron_fins_tester/core/client.py`: UDP/TCP FINS işlemlerini, TCP handshake süreçlerini, güvenli soket kapatmayı, veri tipi dönüştürmelerini (bytes -> float vb.) ve protokol hatalarını (End Code) denetleyen ana istemci (client) yöneticisidir.

## Lisans

Bu proje MIT Lisansı altında sunulmaktadır.
