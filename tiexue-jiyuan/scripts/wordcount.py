import re, sys

fpath = sys.argv[1]
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

parts = content.split('---')
body = '---'.join(parts[2:]) if len(parts) > 2 else content

chinese = len(re.findall(r'[\u4e00-\u9fff]', body))
print(f'中文字数: {chinese}')

last_line = body.rstrip()
last_char = last_line[-1] if last_line else ''
print(f'末尾字符: [{last_char}]')
ends_ok = last_char in '。！？'
print(f'句末完整: {ends_ok}')

if chinese >= 2000 and ends_ok:
    print('PASS')
else:
    if chinese < 2000:
        print(f'FAIL: 字数不足 ({chinese} < 2000)')
    if not ends_ok:
        print(f'FAIL: 句末不完整')
    sys.exit(1)
