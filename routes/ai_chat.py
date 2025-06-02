from flask import render_template, request, jsonify, session
from flask_login import login_required
import json
import os
import google.generativeai as genai
from datetime import datetime
from routes import ai_chat_bp
import config

# Configure Gemini AI
def configure_gemini(api_key):
    """Configure Gemini AI with API key"""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini: {e}")
        return False

def get_gemini_api_key():
    """Get Gemini API key from file"""
    api_key_file = os.path.join(config.DATA_DIR, 'gemini_api_key.txt')
    try:
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading API key: {e}")
    return None

def save_gemini_api_key(api_key):
    """Save Gemini API key to file"""
    api_key_file = os.path.join(config.DATA_DIR, 'gemini_api_key.txt')
    try:
        with open(api_key_file, 'w') as f:
            f.write(api_key)
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False

def preprocess_openstack_data():
    """Preprocess and analyze OpenStack data to create optimized summaries"""
    raw_data = load_raw_openstack_data()
    
    # Debug: Print data loading status
    print(f"DEBUG: Loaded {len(raw_data['instances'])} instances")
    print(f"DEBUG: Loaded {len(raw_data['allocation'])} allocation entries")
    if raw_data['instances']:
        print(f"DEBUG: Sample instance keys: {list(raw_data['instances'][0].keys())}")
    
    # Analyze project resource usage
    project_analysis = analyze_project_resources(raw_data)
    print(f"DEBUG: Project analysis completed for {len(project_analysis)} projects")
    
    # Analyze compute node utilization
    compute_analysis = analyze_compute_utilization(raw_data)
    print(f"DEBUG: Compute analysis completed for {len(compute_analysis)} nodes")
    
    # Analyze resource efficiency
    efficiency_analysis = analyze_resource_efficiency(raw_data)
    
    return {
        'project_analysis': project_analysis,
        'compute_analysis': compute_analysis,
        'efficiency_analysis': efficiency_analysis,
        'raw_summary': raw_data['summary'],
        'debug_info': {
            'instances_loaded': len(raw_data['instances']),
            'allocation_loaded': len(raw_data['allocation']),
            'projects_found': len(project_analysis),
            'compute_nodes_found': len(compute_analysis)
        }
    }

def load_raw_openstack_data():
    """Load raw OpenStack data from files"""
    context = {
        'instances': [],
        'flavors': [],
        'volumes': [],
        'allocation': {},
        'reserved': {},
        'volume_stats': {},
        'ceph_storage': '',
        'placement_diff': [],
        'instance_ids_check': [],
        'ratio_config': [],
        'summary': {}
    }
    
    try:
        # Load instances data (AIO CSV)
        if os.path.exists(config.AIO_CSV_PATH):
            import pandas as pd
            df = pd.read_csv(config.AIO_CSV_PATH, delimiter='|')
            context['instances'] = df.to_dict('records')
        
        # Load flavors data
        if os.path.exists(config.FLAVORS_FILE_PATH):
            import pandas as pd
            df = pd.read_csv(config.FLAVORS_FILE_PATH, delimiter='|')
            context['flavors'] = df.to_dict('records')
        
        # Load volumes data
        if os.path.exists(config.VOLUMES_FILE_PATH):
            with open(config.VOLUMES_FILE_PATH, 'r') as f:
                volumes_data = json.load(f)
                context['volumes'] = volumes_data if isinstance(volumes_data, list) else []
        
        # Load allocation data (compute node resources)
        if os.path.exists(config.ALLOCATION_FILE_PATH):
            with open(config.ALLOCATION_FILE_PATH, 'r') as f:
                allocation_lines = f.readlines()
                allocation_data = []
                for line in allocation_lines:
                    parts = line.strip().split()
                    if len(parts) >= 7:
                        allocation_data.append({
                            'node_id': parts[0],
                            'hostname': parts[1],
                            'type': parts[2],
                            'ip': parts[3],
                            'status': parts[4],
                            'vcpu_used': int(parts[5]),
                            'vcpu_total': int(parts[6]),
                            'memory_used_mb': int(parts[7]) if len(parts) > 7 else 0,
                            'memory_total_mb': int(parts[8]) if len(parts) > 8 else 0
                        })
                context['allocation'] = allocation_data
        
        # Load reserved resources
        if os.path.exists(config.RESERVED_FILE_PATH):
            with open(config.RESERVED_FILE_PATH, 'r') as f:
                context['reserved'] = json.load(f)
        
        # Load volume statistics
        if os.path.exists(config.VOLUME_STATS_FILE_PATH):
            with open(config.VOLUME_STATS_FILE_PATH, 'r') as f:
                context['volume_stats'] = json.load(f)
        
        # Load Ceph storage information
        if os.path.exists(config.CEPHDF_FILE_PATH):
            with open(config.CEPHDF_FILE_PATH, 'r') as f:
                context['ceph_storage'] = f.read()
        
        # Load placement differences
        if os.path.exists(config.PLACEMENT_DIFF_FILE_PATH):
            with open(config.PLACEMENT_DIFF_FILE_PATH, 'r') as f:
                context['placement_diff'] = json.load(f)
        
        # Load instance ID checks
        if os.path.exists(config.INSTANCE_IDS_CHECK_FILE_PATH):
            with open(config.INSTANCE_IDS_CHECK_FILE_PATH, 'r') as f:
                context['instance_ids_check'] = json.load(f)
        
        # Load ratio configuration
        if os.path.exists(config.RATIO_FILE_PATH):
            with open(config.RATIO_FILE_PATH, 'r') as f:
                ratio_lines = f.readlines()
                ratio_data = []
                for line in ratio_lines:
                    parts = line.strip().split(', ')
                    if len(parts) >= 3:
                        ratio_data.append({
                            'hostname': parts[0],
                            'cpu_ratio': float(parts[1]),
                            'memory_ratio': float(parts[2])
                        })
                context['ratio_config'] = ratio_data
        
        # Generate summary statistics
        context['summary'] = {
            'total_instances': len(context['instances']),
            'total_flavors': len(context['flavors']),
            'total_volumes': len(context['volumes']),
            'total_compute_nodes': len(context['allocation']) if isinstance(context['allocation'], list) else 0,
            'projects': list(set([inst.get('Project', 'unknown') for inst in context['instances']])),
            'active_instances': len([inst for inst in context['instances'] if inst.get('Status') == 'ACTIVE']),
            'shutoff_instances': len([inst for inst in context['instances'] if inst.get('Status') == 'SHUTOFF'])
        }
                
    except Exception as e:
        print(f"Error loading OpenStack context: {e}")
    
    return context

def analyze_project_resources(raw_data):
    """Analyze resource usage per project"""
    project_stats = {}
    
    # Group instances by project
    for instance in raw_data['instances']:
        project = instance.get('Project', 'unknown')
        if project not in project_stats:
            project_stats[project] = {
                'instance_count': 0,
                'total_vcpu': 0,
                'total_memory_gb': 0,
                'compute_nodes': set(),
                'instances': []
            }
        
        project_stats[project]['instance_count'] += 1
        # Fix: Use 'CPU' instead of 'vCPUs' and 'RAM' instead of 'Memory' based on CSV header
        vcpu_value = int(instance.get('CPU', 0))
        memory_value = instance.get('RAM', '0G')
        # Handle memory format - could be like '32G', '512M', or just '32'
        if isinstance(memory_value, str):
            if memory_value.endswith('G'):
                memory_gb = float(memory_value.replace('G', ''))
            elif memory_value.endswith('M'):
                memory_gb = float(memory_value.replace('M', '')) / 1024  # Convert MB to GB
            else:
                memory_gb = float(memory_value) if memory_value else 0
        else:
            memory_gb = float(memory_value) if memory_value else 0
        
        project_stats[project]['total_vcpu'] += vcpu_value
        project_stats[project]['total_memory_gb'] += memory_gb
        project_stats[project]['compute_nodes'].add(instance.get('Host', 'unknown'))
        project_stats[project]['instances'].append({
            'name': instance.get('Name', 'unknown'),
            'vcpu': vcpu_value,
            'memory': memory_value,
            'host': instance.get('Host', 'unknown'),
            'status': instance.get('Status', 'unknown')
        })
    
    # Convert sets to lists for JSON serialization
    for project in project_stats:
        project_stats[project]['compute_nodes'] = list(project_stats[project]['compute_nodes'])
    
    return project_stats

def analyze_compute_utilization(raw_data):
    """Analyze compute node utilization with ratio calculations"""
    compute_stats = {}
    
    # Create ratio lookup
    ratio_lookup = {}
    for ratio in raw_data['ratio_config']:
        ratio_lookup[ratio['hostname']] = ratio
    
    # Analyze each compute node
    for node in raw_data['allocation']:
        hostname = node['hostname']
        ratio_info = ratio_lookup.get(hostname, {'cpu_ratio': 4.0, 'memory_ratio': 1.0})
        
        # Calculate actual capacity based on ratio
        base_cpu = 48  # Base physical cores
        actual_cpu_capacity = base_cpu * ratio_info['cpu_ratio']
        
        vcpu_used = node['vcpu_used']
        vcpu_available = actual_cpu_capacity - vcpu_used
        cpu_utilization = (vcpu_used / actual_cpu_capacity) * 100
        
        memory_used_gb = node['memory_used_mb'] / 1024
        memory_total_gb = node['memory_total_mb'] / 1024
        memory_available_gb = memory_total_gb - memory_used_gb
        memory_utilization = (memory_used_gb / memory_total_gb) * 100 if memory_total_gb > 0 else 0
        
        # Find instances on this node
        instances_on_node = [inst for inst in raw_data['instances'] if inst.get('Host') == hostname]
        projects_on_node = list(set([inst.get('Project') for inst in instances_on_node]))
        
        compute_stats[hostname] = {
            'vcpu_used': vcpu_used,
            'vcpu_capacity': actual_cpu_capacity,
            'vcpu_available': vcpu_available,
            'cpu_utilization': round(cpu_utilization, 1),
            'memory_used_gb': round(memory_used_gb, 1),
            'memory_total_gb': round(memory_total_gb, 1),
            'memory_available_gb': round(memory_available_gb, 1),
            'memory_utilization': round(memory_utilization, 1),
            'cpu_ratio': ratio_info['cpu_ratio'],
            'memory_ratio': ratio_info['memory_ratio'],
            'instance_count': len(instances_on_node),
            'projects': projects_on_node,
            'status': 'high_utilization' if cpu_utilization > 90 or memory_utilization > 90 else 'normal'
        }
    
    return compute_stats

def analyze_resource_efficiency(raw_data):
    """Analyze resource efficiency and identify optimization opportunities"""
    analysis = {
        'overutilized_nodes': [],
        'underutilized_nodes': [],
        'resource_waste': {},
        'optimization_opportunities': []
    }
    
    # Analyze compute utilization
    for node in raw_data['allocation']:
        hostname = node['hostname']
        vcpu_used = node['vcpu_used']
        memory_used_mb = node['memory_used_mb']
        memory_total_mb = node['memory_total_mb']
        
        # Calculate utilization percentages
        cpu_util = (vcpu_used / 48) * 100  # Simplified calculation
        memory_util = (memory_used_mb / memory_total_mb) * 100 if memory_total_mb > 0 else 0
        
        if cpu_util > 90 or memory_util > 90:
            analysis['overutilized_nodes'].append({
                'hostname': hostname,
                'cpu_util': round(cpu_util, 1),
                'memory_util': round(memory_util, 1)
            })
        elif cpu_util < 30 and memory_util < 30:
            analysis['underutilized_nodes'].append({
                'hostname': hostname,
                'cpu_util': round(cpu_util, 1),
                'memory_util': round(memory_util, 1),
                'potential_savings': f"Could consolidate {len([inst for inst in raw_data['instances'] if inst.get('Host') == hostname])} instances"
            })
    
    return analysis

@ai_chat_bp.route('/ai-chat')
@login_required
def ai_chat():
    """AI Chat page"""
    api_key = get_gemini_api_key()
    return render_template('ai_chat.html', has_api_key=bool(api_key))

@ai_chat_bp.route('/api/ai-chat/send', methods=['POST'])
@login_required
def send_message():
    """Send message to AI"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get API key
        api_key = get_gemini_api_key()
        if not api_key:
            return jsonify({'error': 'Gemini API key not configured'}), 400
        
        # Configure Gemini
        if not configure_gemini(api_key):
            return jsonify({'error': 'Failed to configure Gemini AI'}), 500
        
        # Get preprocessed OpenStack analysis (optimized for faster AI processing)
        analyzed_data = preprocess_openstack_data()
        
        # Create optimized system prompt with pre-analyzed data
        system_prompt = f"""
Anda adalah AI assistant untuk analisis infrastruktur OpenStack. Anda memiliki akses ke data REAL yang sudah DIANALISIS dari environment OpenStack production.

**INSTRUKSI UTAMA**:
1. SEMUA DATA SUDAH DIPROSES DAN DIANALISIS - Anda TIDAK perlu melakukan perhitungan ulang
2. LANGSUNG BERIKAN KESIMPULAN berdasarkan analisis yang sudah tersedia
3. JANGAN PERNAH bilang "perlu data lebih lengkap", "tidak memiliki informasi", atau "dibutuhkan analisis lebih lanjut"
4. GUNAKAN data yang sudah dianalisis untuk memberikan jawaban spesifik dan actionable

=== ANALISIS PROJECT RESOURCES ===
{json.dumps(analyzed_data['project_analysis'], indent=2)}

=== ANALISIS COMPUTE UTILIZATION ===
{json.dumps(analyzed_data['compute_analysis'], indent=2)}

=== ANALISIS EFISIENSI RESOURCES ===
{json.dumps(analyzed_data['efficiency_analysis'], indent=2)}

=== RINGKASAN ENVIRONMENT ===
{json.dumps(analyzed_data['raw_summary'], indent=2)}

=== DEBUG INFO & STATUS DATA ===
{json.dumps(analyzed_data['debug_info'], indent=2)}

=== KONTEKS TAMBAHAN INFRASTRUKTUR ===
**Konfigurasi Hardware:**
- Base Physical Cores per Node: 48 cores
- CPU Overcommit Ratios: Bervariasi per node (1:1 hingga 1:8)
- Total Compute Nodes: {len(analyzed_data.get('compute_analysis', {}))}

Dalam environment production ini, overcommit ratio yang berbeda digunakan secara strategis:
- **1:1 Ratio**: Digunakan untuk instance production yang membutuhkan resource besar dan performa tinggi
- **1:4 Ratio**: Digunakan untuk instance campuran (mixed workload) dengan kebutuhan resource sedang
- **1:8 Ratio**: Digunakan untuk instance development/testing yang tidak memerlukan resource penuh

Ini adalah praktik normal untuk mengoptimalkan penggunaan resource hardware. Overcommit memungkinkan:
- Efisiensi resource yang lebih baik
- Penghematan biaya infrastruktur
- Fleksibilitas dalam alokasi resource berdasarkan kebutuhan workload

Ketika menganalisis data ratio.txt, perhatikan bahwa variasi ratio ini adalah by design, bukan masalah.

**Detail Kapasitas per Node:**
{chr(10).join([f"- {hostname}: {info['vcpu_capacity']} vCPU capacity (ratio {info['cpu_ratio']}:1), {info['memory_total_gb']}GB RAM" for hostname, info in analyzed_data.get('compute_analysis', {}).items()])}

**Project Distribution:**
{chr(10).join([f"- {project}: {info['instance_count']} instances, {info['total_vcpu']} vCPU, {info['total_memory_gb']:.1f}GB RAM" for project, info in analyzed_data.get('project_analysis', {}).items()])}

**Status Nodes:**
- Normal Utilization: {len([h for h, info in analyzed_data.get('compute_analysis', {}).items() if info.get('status') == 'normal'])}
- High Utilization: {len([h for h, info in analyzed_data.get('compute_analysis', {}).items() if info.get('status') == 'high_utilization'])}

=== PANDUAN RESPONSE CEPAT ===
**UNTUK PERTANYAAN TENTANG PROJECT:**
- Gunakan data dari 'project_analysis' yang sudah menghitung total vCPU, memory, dan instance per project
- Langsung berikan ranking dan perbandingan antar project
- Sertakan breakdown per compute node jika diperlukan

**UNTUK PERTANYAAN TENTANG COMPUTE NODE:**
- Gunakan data dari 'compute_analysis' yang sudah menghitung utilization, capacity, dan availability
- Langsung identifikasi node yang overutilized atau underutilized
- Berikan rekomendasi berdasarkan status yang sudah dianalisis

**UNTUK PERTANYAAN OPTIMASI:**
- Gunakan data dari 'efficiency_analysis' yang sudah mengidentifikasi peluang optimasi
- Langsung berikan rekomendasi konkret berdasarkan analisis yang tersedia

**FORMAT JAWABAN:**
- Langsung berikan kesimpulan di awal
- Sertakan tabel dengan data spesifik
- Berikan rekomendasi actionable
- JANGAN bilang "perlu analisis lebih lanjut" - semua sudah dianalisis!

=== INSTRUKSI KHUSUS ===
**SEMUA PERHITUNGAN SUDAH DILAKUKAN!**
Data dalam 'compute_analysis' sudah mencakup:
- vcpu_capacity (sudah dihitung dengan ratio yang benar)
- vcpu_available (kapasitas - used)
- cpu_utilization (persentase penggunaan)
- memory_available_gb (sudah dikonversi ke GB)
- memory_utilization (persentase penggunaan)
- status (normal/high_utilization)

**LANGSUNG GUNAKAN HASIL ANALISIS:**
- Untuk pertanyaan kapasitas → gunakan vcpu_available dan memory_available_gb
- Untuk pertanyaan utilization → gunakan cpu_utilization dan memory_utilization
- Untuk rekomendasi → gunakan status dan efficiency_analysis

**JANGAN HITUNG ULANG - LANGSUNG JAWAB!**

=== CONTOH RESPONSE YANG DIHARAPKAN ===

**Pertanyaan**: "project apa yang paling banyak pakai vcpu di cloud-node-07?"
**Response yang BENAR**:
"Berdasarkan analisis data yang sudah diproses:

**Project dengan penggunaan vCPU terbanyak di cloud-node-07:**

| Project | Instance Count | Total vCPU | Instances |
|---------|---------------|-------------|----------|
| monitoring-team | 2 | 17 vCPU | monitor-server-alpha, chatbot-app-primary |
| chatbot-service | 1 | 8 vCPU | chatbot-app-primary |

**Kesimpulan**: Project 'monitoring-team' menggunakan vCPU paling banyak (17 vCPU) di cloud-node-07."

**Pertanyaan**: "kenapa project ddb-production boros?"
**Response yang BENAR**:
"Berdasarkan analisis resource project ddb-production:

**Analisis Penggunaan Resource:**
- Total vCPU: X vCPU
- Total Memory: Y GB
- Jumlah Instance: Z
- Tersebar di: [list compute nodes]

**Indikator 'Boros':**
- Ratio vCPU per instance tinggi
- Memory allocation tidak optimal
- Instance placement tidak efisien

**Rekomendasi Optimasi:**
1. [specific recommendation]
2. [specific recommendation]"

**Pertanyaan**: "berapa penggunaan vcpu untuk project ddb-production?"
**Response yang BENAR**:
"Berdasarkan analisis project ddb-production:

**Penggunaan vCPU Project ddb-production:**
- Total vCPU: [angka dari project_analysis]
- Jumlah Instance: [angka dari project_analysis]
- Rata-rata vCPU per Instance: [perhitungan]
- Compute Nodes yang digunakan: [list dari project_analysis]

**Detail per Instance:**
[tabel dengan breakdown per instance]

**Kesimpulan**: Project ddb-production menggunakan total [X] vCPU dari [Y] instances."

**JANGAN PERNAH BILANG:**
❌ "Perlu data lebih lengkap"
❌ "Tidak memiliki informasi"
❌ "Dibutuhkan analisis lebih lanjut"

=== TABLE FORMATTING GUIDELINES ===
**PENTING**: Saat menampilkan data dalam bentuk tabel, gunakan format Markdown yang rapi:

1. **Gunakan Markdown Table Format**:
   ```
   | Column 1 | Column 2 | Column 3 |
   |----------|----------|----------|
   | Data 1   | Data 2   | Data 3   |
   ```

2. **Untuk Data Besar**: Jika tabel terlalu besar, tampilkan hanya data penting atau buat ringkasan

3. **Format Angka**: Gunakan format yang mudah dibaca (contoh: 1,234 MB bukan 1234)

4. **Header yang Jelas**: Gunakan header kolom yang deskriptif

5. **Alignment**: Rata kanan untuk angka, rata kiri untuk teks

6. **Contoh Format yang Baik**:
   | Hostname | vCPU Used | vCPU Total | Utilization |
   |----------|-----------|------------|-------------|
   | cloud-node-01 | 17 | 192 | 8.9% |
   | cloud-node-05 | 189 | 192 | 98.4% |

JANGAN tampilkan data mentah atau format pipe-separated. Selalu gunakan Markdown table yang rapi dan mudah dibaca.

Analyze the provided data comprehensively and provide actionable insights based on the actual infrastructure state.
"""
        
        # Create model and send message with configuration from config
        generation_config = {
            "temperature": config.AI_MODEL_TEMPERATURE,
            "top_p": config.AI_MODEL_TOP_P,
            "top_k": config.AI_MODEL_TOP_K,
            "max_output_tokens": config.AI_MODEL_MAX_TOKENS,
        }
        
        model = genai.GenerativeModel(
            model_name=config.AI_MODEL_NAME,
            generation_config=generation_config
        )
        
        # Combine system prompt with user message
        full_prompt = f"{system_prompt}\n\nUser Question: {message}"
        
        response = model.generate_content(full_prompt)
        
        return jsonify({
            'response': response.text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error in AI chat: {e}")
        return jsonify({'error': f'AI service error: {str(e)}'}), 500

@ai_chat_bp.route('/api/ai-chat/save-api-key', methods=['POST'])
@login_required
def save_api_key():
    """Save Gemini API key"""
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        if save_gemini_api_key(api_key):
            return jsonify({'success': True, 'message': 'API key saved successfully'})
        else:
            return jsonify({'error': 'Failed to save API key'}), 500
            
    except Exception as e:
        print(f"Error saving API key: {e}")
        return jsonify({'error': f'Error saving API key: {str(e)}'}), 500

@ai_chat_bp.route('/api/ai-chat/check-api-key', methods=['GET'])
@login_required
def check_api_key():
    """Check if API key is configured"""
    api_key = get_gemini_api_key()
    return jsonify({'has_api_key': bool(api_key)})