# AI Model Configuration

Konfigurasi model AI sekarang dapat diatur melalui file `config.py` untuk memberikan fleksibilitas dalam mengatur parameter model.

## Parameter Konfigurasi

### AI_MODEL_NAME
- **Default**: `'gemini-2.0-flash'`
- **Deskripsi**: Nama model AI yang akan digunakan
- **Pilihan**: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-1.0-pro`

### AI_MODEL_TEMPERATURE
- **Default**: `0.7`
- **Range**: `0.0 - 2.0`
- **Deskripsi**: Mengontrol kreativitas respons AI. Nilai lebih tinggi = lebih kreatif, nilai lebih rendah = lebih konsisten

### AI_MODEL_MAX_TOKENS
- **Default**: `8192`
- **Range**: `1 - 32768`
- **Deskripsi**: Maksimum token yang dapat dihasilkan dalam satu respons

### AI_MODEL_TOP_P
- **Default**: `0.9`
- **Range**: `0.0 - 1.0`
- **Deskripsi**: Nucleus sampling parameter. Mengontrol keragaman token yang dipilih

### AI_MODEL_TOP_K
- **Default**: `40`
- **Range**: `1 - 100`
- **Deskripsi**: Membatasi jumlah token teratas yang dipertimbangkan untuk setiap langkah

## Cara Mengubah Konfigurasi

1. Buka file `config.py`
2. Ubah nilai parameter sesuai kebutuhan:

```python
# AI Model Configuration
AI_MODEL_NAME = 'gemini-1.5-pro'  # Ganti model
AI_MODEL_TEMPERATURE = 0.5         # Lebih konsisten
AI_MODEL_MAX_TOKENS = 4096         # Respons lebih pendek
AI_MODEL_TOP_P = 0.8               # Sedikit kurang beragam
AI_MODEL_TOP_K = 30                # Lebih fokus
```

3. Restart aplikasi untuk menerapkan perubahan

## Rekomendasi Penggunaan

### Untuk Analisis Teknis (Lebih Akurat)
```python
AI_MODEL_TEMPERATURE = 0.3
AI_MODEL_TOP_P = 0.8
AI_MODEL_TOP_K = 20
```

### Untuk Respons Kreatif (Lebih Fleksibel)
```python
AI_MODEL_TEMPERATURE = 1.0
AI_MODEL_TOP_P = 0.95
AI_MODEL_TOP_K = 60
```

### Untuk Respons Seimbang (Default)
```python
AI_MODEL_TEMPERATURE = 0.7
AI_MODEL_TOP_P = 0.9
AI_MODEL_TOP_K = 40
```

## Catatan

- Perubahan konfigurasi memerlukan restart aplikasi
- Model yang berbeda mungkin memiliki batasan parameter yang berbeda
- Pastikan API key Gemini mendukung model yang dipilih
- Monitor penggunaan token untuk mengoptimalkan biaya API