#!/bin/bash

# 设置超时时间（秒）
TIMEOUT=10

# 通用函数：带超时的 curl 请求
safe_curl() {
    curl -s -m $TIMEOUT "$@"
}

echo "---------------------------------------"
echo "1. Cloudflare (最快)"
cf_loc=$(safe_curl https://www.cloudflare.com/cdn-cgi/trace | grep loc= | cut -d= -f2)
echo "Cloudflare Location: ${cf_loc:-Unknown}"

echo "---------------------------------------"
echo "2. ipinfo.io (详细信息)"
ipinfo=$(safe_curl https://ipinfo.io/json)
ipinfo_country=$(echo "$ipinfo" | grep '"country"' | awk -F '"' '{print $4}')
ipinfo_city=$(echo "$ipinfo" | grep '"city"' | awk -F '"' '{print $4}')
echo "ipinfo.io Country: ${ipinfo_country:-Unknown}"
echo "ipinfo.io City: ${ipinfo_city:-Unknown}"

echo "---------------------------------------"
echo "3. Netflix 国家识别"
netflix_url=$(safe_curl -Ls -o /dev/null -w "%{url_effective}" https://www.netflix.com/title/80018499)
if [[ $netflix_url =~ netflix\.com/([a-z]{2})(-[a-z]{2})?/ ]]; then
    netflix_country="${BASH_REMATCH[1]}"
    echo "Netflix Country: $netflix_country"
else
    echo "Netflix Country: Unknown (URL: $netflix_url)"
fi

echo "---------------------------------------"
echo "4. YouTube Premium 国家检测"
yt_premium=$(safe_curl -L https://www.youtube.com/premium)
if [[ $yt_premium =~ "Premium is available in" ]]; then
    yt_country=$(echo "$yt_premium" | grep -o "Premium is available in [^<]*" | sed 's/Premium is available in //')
    echo "YouTube Premium Country: $yt_country"
else
    echo "YouTube Premium Country: Not Available"
fi

echo "---------------------------------------"
echo "5. Google 搜索页国家识别"
google_ip_page=$(safe_curl -L "https://www.google.com/search?q=my+ip")
if [[ $google_ip_page =~ "你的位置：" ]]; then
    google_location=$(echo "$google_ip_page" | grep -o "你的位置：[^<]*" | sed 's/你的位置：//' | head -n 1)
    echo "Google Location: $google_location"
else
    # 尝试英文版本
    google_ip_page_en=$(safe_curl -L "https://www.google.com/search?q=my+ip&hl=en")
    if [[ $google_ip_page_en =~ "Your location:" ]]; then
        google_location=$(echo "$google_ip_page_en" | grep -o "Your location: [^<]*" | sed 's/Your location: //' | head -n 1)
        echo "Google Location: $google_location"
    else
        echo "Google Location: Unknown (无法识别位置信息)"
    fi
fi

echo "---------------------------------------"
echo "6. Amazon 站点跳转检测"
amazon_url=$(safe_curl -Ls -o /dev/null -w "%{url_effective}" https://www.amazon.com/)
if [[ $amazon_url =~ amazon\.([a-z]{2}) ]]; then
    amazon_country="${BASH_REMATCH[1]}"
    echo "Amazon Country: $amazon_country"
    echo "Amazon Redirect URL: $amazon_url"
else
    echo "Amazon Country: Unknown"
    echo "Amazon Redirect URL: $amazon_url"
fi

echo "---------------------------------------"
echo "7. OpenAI ChatGPT 需要登录（跳过或自行补充 Cookie 调用）"

echo "---------------------------------------"
echo "查询完成"