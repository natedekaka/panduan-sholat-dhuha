import re
import os

file_path = '/home/daniarsyah/apk-nate/panduan_dhuha/android-app/app/src/main/assets/www/index.html'

with open(file_path, 'r') as f:
    content = f.read()

# CSS Variables mapping
replacements = {
    'var(--primary)': '#d4a574',
    'var(--primary-dark)': '#b8956a',
    'var(--secondary)': '#8b7355',
    'var(--bg-dark)': '#1a1a2e',
    'var(--bg-gradient)': 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%)',
    'var(--card-bg)': 'rgba(255, 255, 255, 0.08)',
    'var(--card-border)': 'rgba(212, 165, 116, 0.2)',
    'var(--gold)': '#d4a574',
    'var(--gold-light)': '#e8c9a0',
}

for var, val in replacements.items():
    content = content.replace(var, val)

# Remove :root block
content = re.sub(r':root\s*\{[^}]*\}', '', content)

# Replace ES6 JS features
content = content.replace('const ', 'var ')
content = content.replace('let ', 'var ')
# Arrow functions (simple ones)
content = re.sub(r'(\w+)\s*=>', r'function(\1)', content)
# Backticks
# This is tricky for multiline, but let's try a simple version for single line
content = re.sub(r'`([^`$]*)`', r"'\1'", content)
content = re.sub(r'`([^`$]*)\$\{([^}]*)\}([^`]*)`', r"'\1' + \2 + '\3'", content)

# Fetch replacement (very basic)
fetch_replacement = """
function fetchAPI(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            callback(JSON.parse(xhr.responseText));
        }
    };
    xhr.send();
}
"""

content = content.replace('async function fetchPrayerTimes() {', fetch_replacement + '\nfunction fetchPrayerTimes() {')
# Replace fetch call
content = re.sub(r'var\s+response\s*=\s*await\s+fetch\(([^)]+)\);', r'fetchAPI(\1, function(data) {', content)
content = re.sub(r'var\s+data\s*=\s*await\s+response\.json\(\);', r'', content)
# Close the callback
content = content.replace('if (data.code === 200) {', 'if (data.code === 200) {')
# We need to manually fix the closing brace for the callback, which is hard with regex.
# Let's just rewrite the whole fetchPrayerTimes function.

new_fetch_function = """
        function fetchPrayerTimes() {
            var today = new Date();
            var dateStr = today.toISOString().split('T')[0];
            var url = 'https://api.aladhan.com/v1/timingsByCity?city=Cimahi&country=Indonesia&method=11&date=' + dateStr;
            
            var xhr = new XMLHttpRequest();
            xhr.open('GET', url, true);
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    if (data.code === 200) {
                        var timings = data.data.timings;
                        var sunrise = timings.Sunrise;
                        var dhuhr = timings.Dhuhr;
                        
                        var dhuhaStart = addMinutesToTime(sunrise, 20);
                        var dhuhaEnd = addMinutesToTime(dhuhr, -15);
                        
                        document.getElementById('dhuha-time').innerHTML = dhuhaStart + ' - ' + dhuhaEnd + ' <span style="font-size:14px">WIB</span>';
                        
                        var options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
                        document.getElementById('dhuha-date').textContent = today.toLocaleDateString('id-ID', options);
                        
                        document.querySelector('#prayer-times .prayer-time-item:nth-child(1) .value').textContent = timings.Fajr;
                        document.querySelector('#prayer-times .prayer-time-item:nth-child(2) .value').textContent = timings.Sunrise;
                        document.querySelector('#prayer-times .prayer-time-item:nth-child(3) .value').textContent = timings.Dhuhr;
                        document.querySelector('#prayer-times .prayer-time-item:nth-child(4) .value').textContent = timings.Asr;
                        document.querySelector('#prayer-times .prayer-time-item:nth-child(5) .value').textContent = timings.Maghrib;
                        document.querySelector('#prayer-times .prayer-time-item:nth-child(6) .value').textContent = timings.Isha;
                    }
                }
            };
            xhr.onerror = function() {
                document.getElementById('dhuha-time').innerHTML = '<span style="font-size:16px">07:00 - 11:00 WIB</span>';
            };
            xhr.send();
        }
"""

content = re.sub(r'async function fetchPrayerTimes\(\)\s*\{[\s\S]*?fetchPrayerTimes\(\);', new_fetch_function + '\n        fetchPrayerTimes();', content)

with open(file_path, 'w') as f:
    f.write(content)
