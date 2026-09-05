# Checkout Anomaly Lab

Repository contoh ini sengaja memuat beberapa regresi kecil pada logika bisnis pembayaran.
Tujuannya adalah menghasilkan GitHub Actions failure yang dapat dikumpulkan NAYR sebagai signal
`ci.workflow_run` dengan evidence yang spesifik dan mudah dibedakan satu sama lain.

Tidak ada credential, network call, atau dependency pihak ketiga di project ini.

## Anomaly 1 — Checkout risk boundary (resolved)

Aturan bisnis: transaksi dengan nilai **sama dengan atau melebihi** risk limit harus masuk ke
`manual_review`. Sebelumnya `src/checkout/risk.py` keliru memakai operator `>`, sehingga transaksi
tepat di batas limit justru berstatus `approved`. Anomaly ini sudah diperbaiki (`amount >=
risk_limit`) sehingga workflow `Checkout risk policy` sekarang hijau. Riwayat failure → fix ini
tetap berguna sebagai pasangan evidence before/after.

- workflow: `Checkout risk policy`, job: `test-checkout`, step: `Run checkout policy tests`
- file: `src/checkout/risk.py`

## Anomaly 2 — Refund idempotency (active)

Aturan bisnis: sebuah `refund_id` hanya boleh diproses sekali, dan harus dibandingkan tanpa
memandang huruf besar/kecil. `src/refunds/policy.py` mengecek keanggotaan `refund_id` apa adanya
(case-sensitive), sehingga retry dengan huruf besar/kecil berbeda dianggap `refund_id` baru dan
refund diproses dua kali.

Workflow `Refund idempotency policy` akan menghasilkan evidence berikut:

- failed job: `test-refunds`;
- failed step: `Run refund idempotency tests`;
- lokasi: `src/refunds/policy.py:20`;
- expected: refund `rf-100` diabaikan (duplicate) setelah `RF-100` diproses;
- actual: refund `rf-100` diproses ulang, `total_refunded_cents` menjadi dobel;
- changed file yang dapat dicocokkan: `src/refunds/policy.py`.

### Resolusi

Normalisasi `refund_id` (lowercase) sebelum pengecekan keanggotaan maupun sebelum penyimpanan,
supaya keduanya konsisten:

```python
normalized = refund_id.lower()
if normalized in self.processed_refund_ids:
    return False
self.processed_refund_ids.add(normalized)
```

## Anomaly 3 — Discount rounding (active)

Aturan bisnis: diskon persentase harus dibulatkan ke sen terdekat (round half up).
`src/pricing/discount.py` memotong (truncate) hasil perhitungan alih-alih membulatkannya, sehingga
pelanggan dirugikan satu sen setiap kali pecahan sen hasil diskon `>= 0.5`.

Workflow `Discount rounding policy` akan menghasilkan evidence berikut:

- failed job: `test-pricing`;
- failed step: `Run discount rounding tests`;
- lokasi: `src/pricing/discount.py:25`;
- expected: `discount_cents` 126 untuk harga 1000 sen dengan diskon 12.55%;
- actual: `discount_cents` 125 (dipotong, bukan dibulatkan);
- changed file yang dapat dicocokkan: `src/pricing/discount.py`.

### Resolusi

Ganti pembulatan dari truncation menjadi `ROUND_HALF_UP`:

```python
from decimal import ROUND_HALF_UP

discount_cents = int(raw_discount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
```

## Menjalankan secara lokal

Project membutuhkan Python 3.11 atau lebih baru.

```bash
python -m unittest discover -s tests -v
```

Hasil yang diharapkan saat ini adalah dua test gagal (refund idempotency dan discount rounding);
test checkout risk lulus karena anomaly-nya sudah diperbaiki.

## Memasang sebagai repository GitHub

1. Salin isi folder ini ke repository GitHub baru (jangan menyalin `.git` dari project lain).
2. Commit dan push ke branch default. Ketiga workflow berjalan otomatis pada `push` dan
   `pull_request`.
3. Di NAYR, hubungkan integration GitHub read-only dan pilih repository tersebut.
4. Jalankan sinkronisasi/ingestion setelah workflow selesai.
5. Buka masing-masing signal (`Refund idempotency policy failure`,
   `Discount rounding policy failure`), lalu pilih **Analyze Evidence**.

Token GitHub yang dipakai NAYR perlu akses read-only ke repository serta Actions/Checks agar job,
step, log, dan annotation dapat dikumpulkan. NAYR tidak perlu dan tidak seharusnya diberi akses
write untuk skenario ini.
