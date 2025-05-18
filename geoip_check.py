import gzip
try:
    import brotli
except ImportError:
    brotli = None
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import time
import base64
import urllib.parse
import os
# ---------------------------------------------------------------------------
# ISO‑3166 country name → alpha‑2 code master map (common English names)
# ---------------------------------------------------------------------------
ISO_COUNTRIES = {
    'Afghanistan': 'AF', 'Albania': 'AL', 'Algeria': 'DZ', 'Andorra': 'AD',
    'Angola': 'AO', 'Antigua and Barbuda': 'AG', 'Argentina': 'AR',
    'Armenia': 'AM', 'Australia': 'AU', 'Austria': 'AT', 'Azerbaijan': 'AZ',
    'Bahamas': 'BS', 'Bahrain': 'BH', 'Bangladesh': 'BD', 'Barbados': 'BB',
    'Belarus': 'BY', 'Belgium': 'BE', 'Belize': 'BZ', 'Benin': 'BJ',
    'Bhutan': 'BT', 'Bolivia': 'BO', 'Bosnia and Herzegovina': 'BA',
    'Botswana': 'BW', 'Brazil': 'BR', 'Brunei': 'BN', 'Bulgaria': 'BG',
    'Burkina Faso': 'BF', 'Burundi': 'BI', 'Cabo Verde': 'CV',
    'Cambodia': 'KH', 'Cameroon': 'CM', 'Canada': 'CA',
    'Central African Republic': 'CF', 'Chad': 'TD', 'Chile': 'CL',
    'China': 'CN', 'Colombia': 'CO', 'Comoros': 'KM', 'Congo': 'CG',
    'Costa Rica': 'CR', 'Croatia': 'HR', 'Cuba': 'CU', 'Cyprus': 'CY',
    'Czechia': 'CZ', 'Democratic Republic of the Congo': 'CD',
    'Denmark': 'DK', 'Djibouti': 'DJ', 'Dominica': 'DM',
    'Dominican Republic': 'DO', 'Ecuador': 'EC', 'Egypt': 'EG',
    'El Salvador': 'SV', 'Equatorial Guinea': 'GQ', 'Eritrea': 'ER',
    'Estonia': 'EE', 'Eswatini': 'SZ', 'Ethiopia': 'ET', 'Fiji': 'FJ',
    'Finland': 'FI', 'France': 'FR', 'Gabon': 'GA', 'Gambia': 'GM',
    'Georgia': 'GE', 'Germany': 'DE', 'Ghana': 'GH', 'Greece': 'GR',
    'Grenada': 'GD', 'Guatemala': 'GT', 'Guinea': 'GN',
    'Guinea‑Bissau': 'GW', 'Guyana': 'GY', 'Haiti': 'HT', 'Honduras': 'HN',
    'Hungary': 'HU', 'Iceland': 'IS', 'India': 'IN', 'Indonesia': 'ID',
    'Iran': 'IR', 'Iraq': 'IQ', 'Ireland': 'IE', 'Israel': 'IL',
    'Italy': 'IT', 'Jamaica': 'JM', 'Japan': 'JP', 'Jordan': 'JO',
    'Kazakhstan': 'KZ', 'Kenya': 'KE', 'Kiribati': 'KI', 'Kuwait': 'KW',
    'Kyrgyzstan': 'KG', 'Laos': 'LA', 'Latvia': 'LV', 'Lebanon': 'LB',
    'Lesotho': 'LS', 'Liberia': 'LR', 'Libya': 'LY', 'Liechtenstein': 'LI',
    'Lithuania': 'LT', 'Luxembourg': 'LU', 'Madagascar': 'MG',
    'Malawi': 'MW', 'Malaysia': 'MY', 'Maldives': 'MV', 'Mali': 'ML',
    'Malta': 'MT', 'Marshall Islands': 'MH', 'Mauritania': 'MR',
    'Mauritius': 'MU', 'Mexico': 'MX', 'Micronesia': 'FM', 'Moldova': 'MD',
    'Monaco': 'MC', 'Mongolia': 'MN', 'Montenegro': 'ME', 'Morocco': 'MA',
    'Mozambique': 'MZ', 'Myanmar': 'MM', 'Namibia': 'NA', 'Nauru': 'NR',
    'Nepal': 'NP', 'Netherlands': 'NL', 'New Zealand': 'NZ',
    'Nicaragua': 'NI', 'Niger': 'NE', 'Nigeria': 'NG', 'North Korea': 'KP',
    'North Macedonia': 'MK', 'Norway': 'NO', 'Oman': 'OM', 'Pakistan': 'PK',
    'Palau': 'PW', 'Panama': 'PA', 'Papua New Guinea': 'PG',
    'Paraguay': 'PY', 'Peru': 'PE', 'Philippines': 'PH', 'Poland': 'PL',
    'Portugal': 'PT', 'Qatar': 'QA', 'Romania': 'RO', 'Russia': 'RU',
    'Rwanda': 'RW', 'Saint Kitts and Nevis': 'KN',
    'Saint Lucia': 'LC', 'Saint Vincent and the Grenadines': 'VC',
    'Samoa': 'WS', 'San Marino': 'SM', 'Sao Tome and Principe': 'ST',
    'Saudi Arabia': 'SA', 'Senegal': 'SN', 'Serbia': 'RS', 'Seychelles': 'SC',
    'Sierra Leone': 'SL', 'Singapore': 'SG', 'Slovakia': 'SK',
    'Slovenia': 'SI', 'Solomon Islands': 'SB', 'Somalia': 'SO',
    'South Africa': 'ZA', 'South Korea': 'KR', 'South Sudan': 'SS',
    'Spain': 'ES', 'Sri Lanka': 'LK', 'Sudan': 'SD', 'Suriname': 'SR',
    'Sweden': 'SE', 'Switzerland': 'CH', 'Syria': 'SY', 'Taiwan': 'TW',
    'Tajikistan': 'TJ', 'Tanzania': 'TZ', 'Thailand': 'TH',
    'Timor‑Leste': 'TL', 'Togo': 'TG', 'Tonga': 'TO', 'Trinidad and Tobago': 'TT',
    'Tunisia': 'TN', 'Turkey': 'TR', 'Turkmenistan': 'TM',
    'Tuvalu': 'TV', 'Uganda': 'UG', 'Ukraine': 'UA',
    'United Arab Emirates': 'AE', 'United Kingdom': 'GB',
    'United States': 'US', 'Uruguay': 'UY', 'Uzbekistan': 'UZ',
    'Vanuatu': 'VU', 'Vatican City': 'VA', 'Venezuela': 'VE',
    'Vietnam': 'VN', 'Yemen': 'YE', 'Zambia': 'ZM', 'Zimbabwe': 'ZW',
    'Hong Kong': 'HK', 'Macau': 'MO', 'Åland Islands': 'AX'
}
ISO_COUNTRY_LOOKUP = {k.lower(): v for k, v in ISO_COUNTRIES.items()}
from concurrent.futures import ThreadPoolExecutor, as_completed

class GeoIPChecker:
    def __init__(self, timeout: int = 1, tmp_dir: str = '/tmp/geoip_check/'):
        self.timeout = timeout
        self.session = requests.Session()
        # 配置 SSL 验证
        self.session.verify = True
        # 配置重试策略
        retry_strategy = requests.adapters.Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 默认 User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        # 特定网站的 User-Agent
        self.special_agents = {
            'facebook.com': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'chatgpt.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'chat.openai.com': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
        }
        self.tmp_dir = tmp_dir
        os.makedirs(self.tmp_dir, exist_ok=True)
        # 清理 tmp_dir 下所有旧的 .txt 临时文件
        for fname in os.listdir(self.tmp_dir):
            if fname.endswith('.txt'):
                try:
                    os.remove(os.path.join(self.tmp_dir, fname))
                except Exception as e:
                    print(f"无法删除临时文件 {fname}: {e}")

    def decode_response(self, response):
        """
        自动解压 response 内容，支持 brotli、gzip、deflate，fallback 用 response.text 或 content.decode。
        打印 Content-Encoding 及每一步日志。
        """
        encoding = response.headers.get('Content-Encoding', '').lower()
        print(f"[decode_response] Content-Encoding: {encoding}")
        # 顺序尝试 brotli, gzip, deflate
        # Brotli
        if 'br' in encoding and brotli is not None:
            try:
                decoded = brotli.decompress(response.content).decode('utf-8', errors='replace')
                print("[decode_response] Brotli 解压成功")
                return decoded
            except Exception as e:
                print(f"[decode_response] Brotli 解压失败: {e}")
        # Gzip
        if 'gzip' in encoding:
            try:
                decoded = gzip.decompress(response.content).decode('utf-8', errors='replace')
                print("[decode_response] Gzip 解压成功")
                return decoded
            except Exception as e:
                print(f"[decode_response] Gzip 解压失败: {e}")
        # Deflate
        if 'deflate' in encoding:
            try:
                import zlib
                decoded = zlib.decompress(response.content).decode('utf-8', errors='replace')
                print("[decode_response] Deflate 解压成功")
                return decoded
            except Exception as e:
                print(f"[decode_response] Deflate 解压失败: {e}")
        # 没有 Content-Encoding 或都解压失败，尝试 text
        try:
            print("[decode_response] 使用 response.text")
            return response.text
        except Exception as e:
            print(f"[decode_response] response.text 失败: {e}")
        try:
            print("[decode_response] 使用 response.content.decode('utf-8')")
            return response.content.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"[decode_response] response.content.decode 也失败: {e}")
            print("[decode_response] 返回空字符串")
            return ""

    def save_tmp(self, content, suffix: str):
        """保存内容到临时目录，文件名带时间戳和指定后缀。始终保存为 UTF-8 文本，必要时先 brotli/gzip 解压，打印日志。"""
        ts = time.strftime('%Y%m%d_%H%M%S')
        fname = f"{self.tmp_dir.rstrip('/')}/{ts}_{suffix}"
        text = None
        # 如果已经是 str，直接保存
        if isinstance(content, str):
            print(f"[save_tmp] 内容类型为 str，直接保存到 {fname}")
            text = content
        else:
            # 不是 str，尝试 brotli, gzip, deflate 解压
            print(f"[save_tmp] 内容类型为 {type(content)}, 尝试解压为文本")
            # Brotli
            if brotli is not None:
                try:
                    text = brotli.decompress(content).decode('utf-8', errors='replace')
                    print(f"[save_tmp] Brotli 解压成功，保存到 {fname}")
                except Exception as e:
                    print(f"[save_tmp] Brotli 解压失败: {e}")
            if text is None:
                try:
                    text = gzip.decompress(content).decode('utf-8', errors='replace')
                    print(f"[save_tmp] Gzip 解压成功，保存到 {fname}")
                except Exception as e:
                    print(f"[save_tmp] Gzip 解压失败: {e}")
            if text is None:
                try:
                    import zlib
                    text = zlib.decompress(content).decode('utf-8', errors='replace')
                    print(f"[save_tmp] Deflate 解压成功，保存到 {fname}")
                except Exception as e:
                    print(f"[save_tmp] Deflate 解压失败: {e}")
            if text is None:
                try:
                    text = content.decode('utf-8', errors='replace')
                    print(f"[save_tmp] 直接 decode('utf-8') 成功，保存到 {fname}")
                except Exception as e:
                    print(f"[save_tmp] content.decode 失败: {e}")
                    text = str(content)
                    print(f"[save_tmp] 保存 str(content) 到 {fname}")
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(text)
        except Exception as e:
            print(f"[save_tmp] 写入文件失败: {e}")

    def safe_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """安全的请求方法，包含错误处理"""
        try:
            # 检查是否需要使用特殊的 User-Agent
            for domain, user_agent in self.special_agents.items():
                if domain in url:
                    self.session.headers.update({'User-Agent': user_agent})
                    break
            
            # 设置超时
            kwargs.setdefault('timeout', self.timeout)
            # 禁用重定向，手动处理
            kwargs.setdefault('allow_redirects', False)
            
            response = self.session.request(method, url, **kwargs)
            
            # 处理重定向
            if response.status_code in (301, 302, 303, 307, 308):
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    return self.safe_request(redirect_url, method, **kwargs)
            
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"请求错误 ({url}): {str(e)}")
            return None
        finally:
            # 恢复默认 User-Agent
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            })

    def get_country(self, ip: str) -> str:
        """通过 api.country.is 获取 IP 所属国家（ISO 2 字母）"""
        if not ip or ip.lower() == 'unknown':
            return 'Unknown'
        resp = self.safe_request(f'https://api.country.is/{ip}')
        if resp:
            try:
                return resp.json().get('country', 'Unknown')
            except json.JSONDecodeError:
                return 'Unknown'
        return 'Unknown'

    def check_cloudflare(self) -> Dict[str, Any]:
        """检查 Cloudflare 位置"""
        response = self.safe_request('https://www.cloudflare.com/cdn-cgi/trace')
        if response:
            data = dict(line.split('=') for line in response.text.splitlines())
            return {'location': data.get('loc', 'Unknown')}
        return {'location': 'Unknown'}

    def check_dns_country_match(self) -> Dict[str, Any]:
        """检测公共 IP 与本地 DNS IP 并比较国家是否一致"""
        response = self.safe_request('https://only-185936-14-198-202-48.nstool.onmyojigame.com/')
        if response:
            # 提取两个 IP
            m_ip = re.search(r'Your IP Address:\s*([\d\.]+)', response.text)
            m_dns = re.search(r'Your Local DNS Server:\s*([\d\.]+)', response.text)
            public_ip = m_ip.group(1) if m_ip else 'Unknown'
            dns_ip = m_dns.group(1) if m_dns else 'Unknown'
            public_country = self.get_country(public_ip)
            dns_country = self.get_country(dns_ip)
            return {
                'public_ip': public_ip,
                'public_country': public_country,
                'dns_ip': dns_ip,
                'dns_country': dns_country,
                'match': public_country != 'Unknown' and public_country == dns_country
            }
        return {
            'public_ip': 'Unknown',
            'public_country': 'Unknown',
            'dns_ip': 'Unknown',
            'dns_country': 'Unknown',
            'match': False
        }

    def check_netflix(self) -> Dict[str, Any]:
        """检查 Netflix 国家和可用性（改进）"""
        print("\n3. Netflix 国家识别")
        # 选用一个几乎全球可看的剧集 ID，用于触发地区跳转
        test_title = '80018499'   # House of Cards
        response = self.safe_request(f'https://www.netflix.com/title/{test_title}', allow_redirects=True)
        if not response:
            return {'available': False, 'country': 'Unknown', 'region': 'Unknown'}

        # ① 首选：从最终跳转 URL 中提取地区代码
        final_url = response.url
        region_match = re.search(r'netflix\.com/([a-z]{2}(?:-[a-z]{2})?)/title', final_url)
        if region_match:
            region = region_match.group(1).lower()      # 例如 hk-en、jp、us
            country = region.split('-')[0].upper()      # 取前两位作为国家码
            return {'available': True, 'country': country, 'region': region}

        # ② 备用：尝试解析 nfvdid Cookie（其中包含地区信息）
        nfvdid_cookie = response.cookies.get('nfvdid')
        if nfvdid_cookie:
            try:
                # Cookie 是两段 base64，取第一段做简单解码
                part = nfvdid_cookie.split('%')[0]      # 去掉 URL-encoded 部分尾巴
                decoded = base64.b64decode(urllib.parse.unquote(part)).decode(errors='ignore')
                country_match = re.search(r'"country"\s*:\s*"([A-Z]{2})"', decoded)
                if country_match:
                    country = country_match.group(1)
                    return {'available': True, 'country': country, 'region': country.lower()}
            except Exception:
                pass

        # ③ 如果页面返回 403/404 等错误码，判定为不可用
        if response.status_code in (403, 404):
            return {'available': False, 'country': 'Unknown', 'region': 'Blocked'}

        # ④ 未能识别地区，但服务可访问
        return {'available': True, 'country': 'Unknown', 'region': 'Unknown'}

    def check_youtube_premium(self) -> Dict[str, Any]:
        """检查 YouTube Premium 可用性和地区（增强地区判断）"""
        print("\n4. YouTube Premium 检测")
        premium_response = self.safe_request('https://www.youtube.com/premium', allow_redirects=True)
        if not premium_response:
            return {'available': False, 'country': 'Unknown', 'region': 'Unknown'}
        soup = BeautifulSoup(premium_response.text, 'html.parser')
        # 检查价格信息
        price_text = soup.find(string=re.compile(r'HK\\$|NT\\$|\\$|\\d+\\s*港币|\\d+\\s*新台币|\\d+\\s*USD|\\d+\\s*円|¥'))
        if price_text:
            if 'HK$' in price_text or '港币' in price_text:
                return {'available': True, 'country': 'HK', 'region': 'Hong Kong'}
            elif 'NT$' in price_text or '新台币' in price_text:
                return {'available': True, 'country': 'TW', 'region': 'Taiwan'}
            elif 'USD' in price_text or '$' in price_text:
                return {'available': True, 'country': 'US', 'region': 'United States'}
            elif '円' in price_text or '¥' in price_text:
                return {'available': True, 'country': 'JP', 'region': 'Japan'}
        # 检查地区限制提示
        region_text = soup.find(string=re.compile(r'not available|unavailable|不可用|利用できません|사용할 수 없음'))
        if region_text:
            return {'available': False, 'country': 'Unknown', 'region': 'Blocked'}
        return {'available': True, 'country': 'Unknown', 'region': 'Unknown'}

    def check_google_location(self) -> dict:
        print("\n5. Google 位置检测")
        # 设置更真实的浏览器特征
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-HK,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # 只请求 Google 主页
        home_resp = self.safe_request('https://www.google.com.hk/?hl=zh-HK', headers=headers, allow_redirects=True)
        if not home_resp:
            return {'location': 'Unknown', 'method': 'unknown'}
        
        # 确保响应内容被正确解码
        try:
            if 'br' in home_resp.headers.get('Content-Encoding', '').lower():
                if brotli is not None:
                    html_content = brotli.decompress(home_resp.content).decode('utf-8', errors='replace')
                else:
                    html_content = home_resp.text
            elif 'gzip' in home_resp.headers.get('Content-Encoding', '').lower():
                html_content = gzip.decompress(home_resp.content).decode('utf-8', errors='replace')
            else:
                html_content = home_resp.text
        except Exception as e:
            print(f"[DEBUG] 解码响应内容时出错: {e}")
            html_content = home_resp.text
        
        ts = time.strftime('%Y%m%d_%H%M%S')
        self.save_tmp(html_content, f'google_home_html_{ts}.txt')
        
        # 方法3：从主页底部文本中提取位置信息
        soup = BeautifulSoup(html_content, "html.parser")
        menu_words = {
            'about', 'advertising', 'business', 'how search works', 'privacy', 'terms',
            'settings', 'advertise', 'store', 'all', 'images', 'videos', 'news', 'shopping',
            'tools', 'search', 'sign in', 'gmail', 'more', 'maps', 'play', 'youtube', 'drive',
            'calendar', 'translate', 'photos', 'books', 'blogger', 'contacts', 'docs', 'finance',
            'groups', 'hangouts', 'keep', 'meet', 'jamboard', 'earth', 'chrome', 'arts & culture',
            'podcasts', 'stadia', 'duo', 'messages', 'collections', 'forms', 'ads', 'developers',
            'press', 'location', 'account', 'help', 'send feedback', 'learn more', 'cookies'
        }
        
        # 收集所有可能的短文本
        short_texts = set()
        for tag in soup.find_all(['div', 'span', 'p', 'a']):
            txt = tag.get_text(separator=' ', strip=True)
            if txt and len(txt) <= 30:
                t = txt.lower()
                if t and t not in menu_words and not re.fullmatch(r'\s*', t):
                    short_texts.add(t)
        
        print("[DEBUG] 提取到的短文本候选内容:", short_texts)
        print("[DEBUG] 用于匹配的国家名:", list(ISO_COUNTRY_LOOKUP.keys())[:10], "... 共", len(ISO_COUNTRY_LOOKUP))
        
        # 尝试匹配国家名
        for text in short_texts:
            for name_lower, code in ISO_COUNTRY_LOOKUP.items():
                if name_lower in text:
                    print(f"[DEBUG] 命中：{text} => {name_lower} => {code}")
                    return {'location': code, 'country': name_lower.title(), 'method': 'bottom_text'}
        
        # 如果从文本中没有找到位置信息，尝试从 URL 中获取
        if 'google.com.hk' in home_resp.url:
            return {'location': 'HK', 'country': 'Hong Kong', 'method': 'url'}
        
        print("[DEBUG] 未匹配到任何国家名，返回 Unknown")
        return {'location': 'Unknown', 'method': 'bottom_text'}

    def check_amazon(self) -> Dict[str, Any]:
        """检查 Amazon 重定向"""
        response = self.safe_request('https://www.amazon.com/', allow_redirects=True)
        if response:
            match = re.search(r'amazon\.([a-z]{2})', response.url)
            if match:
                return {'country': match.group(1).upper(), 'url': response.url}
        return {'country': 'Unknown', 'url': 'Unknown'}

    def check_disney_plus(self) -> Dict[str, Any]:
        """检查 Disney+ 国家或可用性"""
        print("\n7. Disney+ 检测")
        response = self.safe_request('https://www.disneyplus.com/', allow_redirects=True)
        if not response:
            return {'available': False, 'region': 'Unknown'}
        # 检查返回的physical-location
        physical_location = response.headers.get('physical-location')
        if physical_location:
            return {'available': True, 'region': physical_location}
        return {'available': True, 'region': 'Unknown'}

    def check_x(self) -> Dict[str, Any]:
        """检查 X (Twitter) 可用性"""
        response = self.safe_request('https://twitter.com/', allow_redirects=True)
        if response and response.status_code == 200:
            return {'available': True}
        return {'available': False}

    def check_tiktok(self) -> Dict[str, Any]:
        """检查 TikTok 可用性"""
        response = self.safe_request('https://www.tiktok.com/', allow_redirects=True)
        if response and response.status_code == 200:
            return {'available': True}
        return {'available': False}

    def check_openai(self) -> Dict[str, Any]:
        """检查 OpenAI ChatGPT 可用性及地区（Cloudflare trace）"""
        print("\n10. OpenAI (chat.openai.com) 可用性检测")
        trace_resp = self.safe_request('https://chat.openai.com/cdn-cgi/trace')
        if not trace_resp:
            # 尝试备用域名 chatgpt.com
            trace_resp = self.safe_request('https://chatgpt.com/cdn-cgi/trace')
        if trace_resp:
            data = dict(line.split('=') for line in trace_resp.text.splitlines() if '=' in line)
            loc = data.get('loc', 'Unknown')
            # 若出现 warp=deny 表示被 Cloudflare 拦截
            blocked = data.get('warp') == 'deny' or data.get('ip') is None
            return {'available': not blocked, 'country': loc}
        # 请求都失败，视为不可用
        return {'available': False, 'country': 'Unknown'}

    def check_facebook(self) -> Dict[str, Any]:
        """检查 Facebook 可用性（多端点尝试）"""
        test_urls = [
            'https://www.facebook.com/favicon.ico',
            'https://m.facebook.com/favicon.ico',
            'https://graph.facebook.com/robots.txt'
        ]
        for url in test_urls:
            resp = self.safe_request(url, allow_redirects=True)
            if resp and resp.status_code == 200:
                return {'available': True}
        return {'available': False}

    def check_instagram(self) -> Dict[str, Any]:
        """检查 Instagram 可用性"""
        response = self.safe_request('https://www.instagram.com/', allow_redirects=True)
        if response and response.status_code == 200:
            return {'available': True}
        return {'available': False}

    def check_telegram(self) -> Dict[str, Any]:
        """检查 Telegram 可用性"""
        response = self.safe_request('https://web.telegram.org/', allow_redirects=True)
        if response and response.status_code == 200:
            return {'available': True}
        return {'available': False}

    def run_all_checks(self):
        """运行所有检查"""
        print("开始检测地理位置信息...")
        print("---------------------------------------")
        
        # 使用线程池并行执行检查
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.check_cloudflare): "Cloudflare",
                executor.submit(self.check_dns_country_match): "DNSMatch",
                executor.submit(self.check_netflix): "Netflix",
                executor.submit(self.check_youtube_premium): "YouTube",
                executor.submit(self.check_google_location): "Google",
                executor.submit(self.check_amazon): "Amazon",
                executor.submit(self.check_disney_plus): "DisneyPlus",
                executor.submit(self.check_x): "X",
                executor.submit(self.check_tiktok): "TikTok",
                executor.submit(self.check_openai): "OpenAI",
                executor.submit(self.check_facebook): "Facebook",
                executor.submit(self.check_instagram): "Instagram",
                executor.submit(self.check_telegram): "Telegram"
            }
            
            results = {}
            for future in as_completed(futures):
                service = futures[future]
                try:
                    results[service] = future.result()
                except Exception as e:
                    print(f"{service} 检查失败: {str(e)}")
                    results[service] = None

        # 按顺序输出结果
        print("1. Cloudflare (最快)")
        print(f"Cloudflare Location: {results['Cloudflare']['location']}")
        print("---------------------------------------")

        print("2. DNS & 本地解析服务器检测")
        dns_result = results['DNSMatch']
        print(f"Public IP: {dns_result['public_ip']} ({dns_result['public_country']})")
        print(f"DNS IP   : {dns_result['dns_ip']} ({dns_result['dns_country']})")
        if dns_result['match']:
            print("✅ 公网 IP 与 DNS 服务器属于同一国家")
        else:
            print("⚠️  公网 IP 与 DNS 服务器国家不一致")
        print("---------------------------------------")

        print("3. Netflix 国家识别")
        if results['Netflix']['available']:
            print(f"Netflix 地区: {results['Netflix']['region']} ({results['Netflix']['country']})")
        else:
            print("Netflix: Not Available")
        print("---------------------------------------")

        print("4. YouTube Premium 国家检测")
        if results['YouTube']['available']:
            print(f"YouTube Premium 地区: {results['YouTube']['region']} ({results['YouTube']['country']})")
        else:
            print("YouTube Premium: Not Available")
        print("---------------------------------------")

        print("5. Google 位置检测")
        print(f"Google Location: {results['Google']['location']}")
        print("---------------------------------------")

        print("6. Amazon 站点跳转检测")
        print(f"Amazon Country: {results['Amazon']['country']}")
        print(f"Amazon URL: {results['Amazon']['url']}")
        print("---------------------------------------")

        print("7. Disney+ 检测")
        if results['DisneyPlus']['available']:
            print(f"Disney+ Region: {results['DisneyPlus']['region']}")
        else:
            print("Disney+: Not Available")
        print("---------------------------------------")

        print("8. X (Twitter) 可用性检测")
        print(f"X (Twitter): {'Available' if results['X']['available'] else 'Not Available'}")
        print("---------------------------------------")

        print("9. TikTok 可用性检测")
        print(f"TikTok: {'Available' if results['TikTok']['available'] else 'Not Available'}")
        print("---------------------------------------")

        print("10. OpenAI (chat.openai.com) 可用性检测")
        if results['OpenAI']['available']:
            print(f"OpenAI Country: {results['OpenAI']['country']} (Available)")
        else:
            print("OpenAI: Not Available")
        print("---------------------------------------")

        print("11. Facebook 可用性检测")
        print(f"Facebook: {'Available' if results['Facebook']['available'] else 'Not Available'}")
        print("---------------------------------------")

        print("12. Instagram 可用性检测")
        print(f"Instagram: {'Available' if results['Instagram']['available'] else 'Not Available'}")
        print("---------------------------------------")

        print("13. Telegram 可用性检测")
        print(f"Telegram: {'Available' if results['Telegram']['available'] else 'Not Available'}")
        print("---------------------------------------")

        print("所有检查完成")

if __name__ == "__main__":
    checker = GeoIPChecker()
    checker.run_all_checks() 