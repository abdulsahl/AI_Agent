import os
import json
import google.generativeai as genai

from prompt_template import PROFESSOR_SAHL_PROMPT_TEMPLATE


# Google API key.
GOOGLE_API_KEY = "" 
CHAT_HISTORY_DIR = "chat_history" 


def save_chat_session(session_name, content):
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{session_name}.json")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"[SYSTEM: ✅ Obrolan '{session_name}' berhasil disimpan.]"
    except Exception as e:
        return f"[SYSTEM ERROR: Gagal menyimpan obrolan '{session_name}': {e}]"

def load_chat_session(session_name):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{session_name}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            json.loads(content) 
            return content
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"[SYSTEM WARNING: File '{session_name}.json' rusak dan bukan JSON yang valid. State baru akan dibuat.]")
        return None
    except Exception as e:
        print(f"[SYSTEM ERROR: Gagal memuat obrolan '{session_name}': {e}]")
        return None

def delete_chat_session(session_name):
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{session_name}.json")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"[SYSTEM: 🧹 Obrolan '{session_name}' berhasil dihapus.]"
        else:
            return f"[SYSTEM: ⚠️ Obrolan '{session_name}' tidak ditemukan.]"
    except Exception as e:
        return f"[SYSTEM ERROR: Gagal menghapus obrolan '{session_name}': {e}]"

def list_chat_sessions():
    if not os.path.exists(CHAT_HISTORY_DIR) or not os.listdir(CHAT_HISTORY_DIR):
        return "[SYSTEM: 📂 Tidak ada obrolan yang tersimpan.]"
    
    files = [f.replace('.json', '') for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith('.json')]
    return "[SYSTEM: 📂 Daftar obrolan yang tersedia:]\n- " + "\n- ".join(files)

if not GOOGLE_API_KEY or "GANTI_DENGAN_API_KEY_ANDA" in GOOGLE_API_KEY:
    print("❌ [ERROR] GOOGLE_API_KEY belum diisi dengan benar. Harap masukkan API key Anda di dalam skrip.")
    exit()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
except Exception as e:
    print(f"❌ [ERROR] Gagal mengkonfigurasi Google AI. Pastikan API Key valid. Kesalahan: {e}")
    exit()

# State awal yang bersih
initial_reasoning_state = { "Reasoning": {} }
initial_reasoning_json = json.dumps(initial_reasoning_state, indent=2)

previous_reasoning_json = initial_reasoning_json
current_session_name = None

# --- MAIN LOOP ---

print("🧙🏾‍♂️: Hello, I am Professor Sahl! 👋🏾")
print("Saya menggunakan 'Reasoning' untuk membantu Anda mencapai tujuan.")
print("Ketik 'help' untuk melihat perintah yang tersedia atau 'exit' untuk keluar.")

while True:
    # Menampilkan nama sesi aktif jika ada
    prompt_indicator = f"[{current_session_name}] Anda: " if current_session_name else "Anda: "
    user_input = input(f"\n{prompt_indicator}")
    
    # Menangani perintah internal
    command_parts = user_input.strip().lower().split()
    command = command_parts[0] if command_parts else ""

    if command == "exit":
        print("🧙🏾‍♂️: Farewell! May your journey be filled with discovery.")
        break
    
    elif command == "help":
        print("""[SYSTEM: Perintah yang tersedia:]
- new <nama_obrolan>   : Memulai obrolan baru.
- load <nama_obrolan>  : Memuat obrolan yang sudah ada.
- save <nama_baru>     : Menyimpan obrolan saat ini dengan nama baru (menduplikasi).
- list                 : Menampilkan semua obrolan yang tersimpan.
- delete <nama_obrolan>: Menghapus obrolan.
- help                 : Menampilkan bantuan ini.
- exit                 : Keluar dari program.""")
        continue

    elif command == "new":
        if len(command_parts) > 1:
            current_session_name = command_parts[1]
            previous_reasoning_json = initial_reasoning_json
            print(f"[SYSTEM: 🚀 Memulai obrolan baru dengan nama '{current_session_name}'.]")
            # Simpan file kosong untuk menandai sesi baru
            save_chat_session(current_session_name, previous_reasoning_json)
        else:
            print("[SYSTEM: ⚠️ Harap berikan nama untuk obrolan baru. Contoh: new obrolan_pertama]")
        continue

    elif command == "load":
        if len(command_parts) > 1:
            session_to_load = command_parts[1]
            loaded_json = load_chat_session(session_to_load)
            if loaded_json:
                previous_reasoning_json = loaded_json
                current_session_name = session_to_load
                print(f"[SYSTEM: ✅ Obrolan '{current_session_name}' berhasil dimuat.]")
            else:
                print(f"[SYSTEM: ⚠️ Gagal memuat. Obrolan '{session_to_load}' tidak ditemukan atau rusak.]")
        else:
            print("[SYSTEM: ⚠️ Harap berikan nama obrolan yang akan dimuat. Contoh: load obrolan_pertama]")
        continue
    
    elif command == "list":
        print(list_chat_sessions())
        continue

    elif command == "delete":
        if len(command_parts) > 1:
            session_to_delete = command_parts[1]
            print(delete_chat_session(session_to_delete))
            if current_session_name == session_to_delete:
                current_session_name = None
                previous_reasoning_json = initial_reasoning_json
                print("[SYSTEM: ⚠️ Obrolan aktif telah dihapus. Silakan mulai 'new' atau 'load' obrolan lain.]")
        else:
            print("[SYSTEM: ⚠️ Harap berikan nama obrolan yang akan dihapus. Contoh: delete obrolan_pertama]")
        continue
    
    elif command == "save":
        if not current_session_name:
            print("[SYSTEM: ⚠️ Tidak ada obrolan aktif untuk disimpan. Mulai dengan 'new' atau 'load' terlebih dahulu.]")
            continue
        if len(command_parts) > 1:
            new_name = command_parts[1]
            print(save_chat_session(new_name, previous_reasoning_json))
            current_session_name = new_name # Otomatis beralih ke sesi yang baru disimpan
            print(f"[SYSTEM: Beralih ke sesi aktif '{current_session_name}'.]")
        else:
            print("[SYSTEM: ⚠️ Harap berikan nama baru untuk menyimpan obrolan. Contoh: save salinan_obrolan]")
        continue
        
    # Jika tidak ada sesi aktif, paksa pengguna untuk membuat/memuat sesi
    if not current_session_name:
        print("\n[SYSTEM: ⚠️ Tidak ada obrolan aktif. Silakan mulai obrolan baru atau muat yang sudah ada.]")
        print("[Contoh: 'new proyek_alpha' atau 'load obrolan_lama']")
        continue

    print("\n[SYSTEM: Professor Sahl is thinking... 🧠]")

    try:
        prompt = PROFESSOR_SAHL_PROMPT_TEMPLATE.format(
            user_input=user_input,
            previous_reasoning_json=previous_reasoning_json
        )

        raw_response_text = model.generate_content(prompt).text
        print(raw_response_text)

        # Proses internal untuk mengekstrak JSON dan memperbarui state
        json_start_tag = '```json'
        json_end_tag = '```'
        json_start_index = raw_response_text.find(json_start_tag)
        json_end_index = raw_response_text.find(json_end_tag, json_start_index + 1)

        if json_start_index != -1 and json_end_index != -1:
            json_str_to_parse = raw_response_text[json_start_index + len(json_start_tag) : json_end_index].strip()
            
            try:
                current_reasoning_obj = json.loads(json_str_to_parse)
                previous_reasoning_json = json.dumps(current_reasoning_obj, indent=2)

                # >>> AUTO-SAVE SETELAH SETIAP INTERAKSI <<<
                save_chat_session(current_session_name, previous_reasoning_json)

            except json.JSONDecodeError:
                print("[SYSTEM WARNING: Model tidak menghasilkan JSON yang valid. State tidak diperbarui.]")
                
    except Exception as e:
        print(f"[SYSTEM ERROR: ❌ Terjadi kesalahan. Error: {e}]")
        if 'raw_response_text' in locals():
            print("--- Raw Model Output ---")
            print(raw_response_text)
            print("------------------------")
        continue
