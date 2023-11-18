from assets.utils import *
import requests
import string
import sys
import re

PORT = 8080

def regex(_content, rexexpfile):
    with open(rexexpfile, 'r') as f:
        _rexexp = f.read()
    
    content = _content.translate({ord(c): None for c in string.whitespace})
    rexexp = _rexexp.translate({ord(c): None for c in string.whitespace})

    reger = re.compile(r'{}'.format(rexexp))
    match = reger.match(content)
    assert(match)

    # print(f"{rexexp = }")
    # print(f"{content = }")
    
    return match.groups()

def parseTable(html):
    table = html[html.find("<tbody>")+7:html.rfind("</tbody>")].strip()
    # print(table)

    items = {}
    rows = table.split("<tr><td>")
    for r in rows:
        row = r.strip()
        if row == "":
            continue

        # print(row)
        reger = re.compile(r'<a href=\"([\w\W]+)\">([\w\W]+)</a></td></tr>')
        match = reger.match(row)
        href = match.groups()[0]
        text = match.groups()[1]
        
        items[text] = href

    return(items)

def uploadFile(filename):
    return {'upfile': open(filename,'rb')}

if __name__ == '__main__':
    if len(sys.argv) == 2:
        PORT = sys.argv[1]
    elif len(sys.argv) > 2:
        print("Invalid arguments.")
        exit(1)
        
    if not os.path.exists('assets/files'):
        os.makedirs('assets/files')
    genFile('assets/files/afile', size='10M')

    req = requests.get(f'http://localhost:{PORT}/')
    assert(req.status_code == 200)
    name, id = regex(req.content.decode(), 'assets/index.html')
    print(f"{name = } {id = }")

    req = requests.post(f'http://localhost:{PORT}/api/file', files=uploadFile('assets/files/afile'))
    assert(req.status_code == 401)

    req = requests.post(f'http://localhost:{PORT}/api/file', files=uploadFile('assets/files/afile'), auth=requests.auth.HTTPBasicAuth('demo', '123'))
    assert(req.status_code == 200)
    cmpFile('assets/files/afile', '../hw2/web/files/afile')

    req = requests.post(f'http://localhost:{PORT}/api/file', files=uploadFile('assets/files/afile'))
    assert(req.status_code == 401)

    req = requests.get(f'http://localhost:{PORT}/file/')
    assert(req.status_code == 200)
    regex(req.content.decode(), 'assets/listf.rhtml')
    fileList = parseTable(req.content.decode())
    print(f"{fileList = }")
    assert(fileList == {'afile': '/api/file/afile'})

    req = requests.get(f'http://localhost:{PORT}/video/')
    assert(req.status_code == 200)
    regex(req.content.decode(), 'assets/listv.rhtml')
    videoList = parseTable(req.content.decode())
    print(f"{videoList = }")
    assert(videoList == {})

