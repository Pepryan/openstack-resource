# AI Chat Feature - OpenStack Manager

## Overview
Fitur AI Chat telah berhasil ditambahkan ke aplikasi OpenStack Manager. Fitur ini menggunakan Google Gemini AI untuk memberikan insights, analisis, dan rekomendasi berdasarkan data infrastruktur OpenStack Anda.

## Features

### 🤖 AI Assistant Capabilities
- **Resource Utilization Analysis**: Analisis penggunaan resource saat ini
- **Performance Optimization**: Rekomendasi optimasi performa
- **Cost Analysis**: Analisis dan optimasi biaya
- **Capacity Planning**: Perencanaan kapasitas berdasarkan tren
- **Migration Suggestions**: Saran migrasi instance
- **Infrastructure Health Assessment**: Penilaian kesehatan infrastruktur

### 🔧 Technical Features
- **Google Gemini AI Integration**: Menggunakan model gemini-flash-2.0
- **OpenStack Context Awareness**: AI memiliki akses ke data OpenStack real-time
- **Secure API Key Management**: API key disimpan secara aman di file lokal
- **Responsive Design**: UI yang responsif untuk desktop dan mobile
- **Real-time Chat Interface**: Interface chat yang modern dan interaktif

## Setup Instructions

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Get Google Gemini API Key
1. Kunjungi [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Buat API key gratis
3. Simpan API key untuk konfigurasi

### 3. Configure API Key
1. Jalankan aplikasi
2. Buka halaman AI Chat
3. Masukkan API key di bagian konfigurasi
4. Klik "Save" untuk menyimpan

### 4. Start Using AI Chat
- Akses melalui menu "AI Chat" di navbar
- Gunakan quick questions atau ketik pertanyaan custom
- AI akan memberikan insights berdasarkan data OpenStack Anda

## File Structure

```
├── routes/
│   └── ai_chat.py              # Backend routes untuk AI chat
├── templates/
│   └── ai_chat.html            # Template HTML untuk halaman chat
├── static/
│   ├── ai-chat.css             # Styling untuk AI chat
│   └── ai-chat.js              # JavaScript untuk interaksi chat
├── data/
│   └── gemini_api_key.txt      # File penyimpanan API key (auto-created)
└── requirements.txt            # Dependencies (updated)
```

## API Endpoints

### GET `/ai-chat`
Halaman utama AI chat

### POST `/api/ai-chat/send`
Mengirim pesan ke AI
```json
{
  "message": "What is the current resource utilization?"
}
```

### POST `/api/ai-chat/save-api-key`
Menyimpan API key Gemini
```json
{
  "api_key": "your-gemini-api-key"
}
```

### GET `/api/ai-chat/check-api-key`
Mengecek status API key

## Quick Questions Examples

1. **Resource Utilization**: "What is the current resource utilization of my OpenStack environment?"
2. **Performance Analysis**: "Can you analyze the performance of my instances and suggest optimizations?"
3. **Cost Optimization**: "What are the cost optimization opportunities in my infrastructure?"
4. **Capacity Planning**: "Do I need to plan for capacity expansion based on current trends?"
5. **Migration Suggestions**: "Which instances should I consider migrating and why?"
6. **Health Check**: "What is the overall health status of my OpenStack infrastructure?"

## Data Context

AI memiliki akses ke data OpenStack berikut:
- **Instances**: Data dari aio.csv (10 instance terbaru)
- **Flavors**: Data flavor dari flavors.csv (10 flavor terbaru)
- **Volumes**: Data volume dari volumes.json (10 volume terbaru)
- **Allocation**: Informasi alokasi resource
- **Reserved**: Data resource yang direservasi

## Security Considerations

- API key disimpan di file lokal (`data/gemini_api_key.txt`)
- Tidak ada data sensitif yang dikirim ke Google Gemini
- Hanya metadata dan statistik yang dibagikan untuk analisis
- Akses dibatasi dengan Flask-Login authentication

## Troubleshooting

### API Key Issues
- Pastikan API key valid dan aktif
- Cek quota API di Google AI Studio
- Pastikan file `data/gemini_api_key.txt` dapat ditulis

### Connection Issues
- Pastikan koneksi internet stabil
- Cek firewall settings
- Verifikasi dependencies terinstall dengan benar

### Data Issues
- Pastikan file data OpenStack tersedia di folder `data/`
- Cek format file CSV dan JSON
- Verifikasi permissions file

## Future Enhancements

- [ ] Database integration untuk menyimpan chat history
- [ ] Multiple AI model support
- [ ] Advanced analytics dan reporting
- [ ] Export chat conversations
- [ ] Custom AI prompts dan templates
- [ ] Integration dengan OpenStack APIs langsung

## Support

Untuk pertanyaan atau issues, silakan buat issue di repository atau hubungi tim development.