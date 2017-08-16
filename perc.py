from flask import Flask, abort, send_from_directory, request
from os import listdir
import markdown
from os.path import isfile, join, isdir
import os
#PREFIX="site/"
app = Flask(__name__)
app.config['DEBUG'] = True

tmpl = """<!doctype html>
<html>
<head>
<link rel="stylesheet" href="/pub/site.css">
<title>{title}</title>
</head>
<body>
<!--<div id="topbar">{topbar}</div>
<header><h1><a href="/">{site_title}</a></h1> <span id="subtitle">{subtitle}</span></header>

<nav id="sidebar">{nav}</nav>
<article id="content">{content}</article>
<footer>{footer}</footer>-->

<div class="wrap">
<div class="grid">
<div class="grid__col grid__col--2-of-4 grid__col--centered">
<!--{topbar}-->
</div>
<div class="grid__col grid__col--2-of-4 grid__col--centered">
<h1 id="sitetitle"><a href="/">{site_title}</a></h1> <span id="subtitle">{subtitle}</span>
</div>
</div>

<div class="grid">
        <div class="grid__col grid__col--1-of-4">

        </div>
        <div class="grid__col grid__col--3-of-4" id="head">

        </div>    
</div>

<div class="grid">
        <div class="grid__col grid__col--1-of-4" id="sidebar">
{nav}
        </div>
        <div class="grid__col grid__col--3-of-4" id="content">
{content}

        </div>    
</div>

<div class="grid">
        <div class="grid__col grid__col--1-of-4">

        </div>
        <div class="grid__col grid__col--3-of-4" id="foot">

{footer}

        </div>    
</div>



</div>

</body>
</html>"""

def navclear(s):
    if s.endswith(".md"):
        return s[:-3]
    if s.endswith(".html"):
        return s[:-5]
    if s.endswith(".txt"):
        return s[:-4]
    return s

def navii(loc, n, parent, donext):
    parts = loc.split('/')
    cur = '/'.join(parts[:n+1])
    print(cur)
    out = ''
    if n==0:
        out += "<ul>"
    if(isdir(cur)):
        for i in listdir(cur):
            if i[0] != '.' and not i.endswith('~') and not (i.startswith('#') and i.endswith('#')) and not (n==0 and i in ["pub", "favicon.ico", "robots.txt"]): # don't show hidden files
                if cur+'/'+i=='/'.join(parts):
                    print("INSIDE "+cur+" AT "+i+" and donext is "+str(donext)+" and parts is "+str(parts))
                    #out += "<li><i>"+i+"</i>"
                    out += "<li><a href=\""+parent+"\" class=\"selected\">"+navclear(i.replace('_', ' '))+"</a>"
                    if donext:
                        out += "<ul>"+navii(loc, n+1, parent+'/'+i, False)+"</ul>"
                    out += "</li>"
                else:
                    print("INSIDE "+cur+" AT "+i+" and donext is "+str(donext)+" and parts is "+str(parts))
                    if i=="index.md" and isfile(cur+'/index.md'):
                        pass
                    else:
                        if navclear(i)==parts[len(parts)-1] and n==len(parts)-2:
                            out += "<li><a href=\""+parent+'/'+navclear(i)+"\" class=\"selected\">"+navclear(i.replace('_', ' '))+"</a>"
                        else:
                            out += "<li><a href=\""+parent+'/'+navclear(i)+"\">"+navclear(i.replace('_', ' '))+"</a>"
                        if donext:
                            if i == parts[n+1] and isdir('/'.join(parts[:n+1])):
                                out += "<ul>"+navii(loc, n+1, parent+'/'+navclear(i), True)+"</ul>"
                        out += "</li>"
    if n==0:
        out += "</ul>"
    return out

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def page(path):
    PREFIX=request.environ['HOST']+"/"
    #PREFIX="localhost/"
    if not os.path.exists(PREFIX+".info"):
        abort(500)
    info = []
    with open(PREFIX+".info", 'r') as infile:
        for line in infile:
            info.append(line)
    #return path
    path = path.replace('../', '/')
    path = path.replace('./', '/')
    s = ""
    ptitle = ""
    print("r: "+path)
    print(PREFIX+path+" is a dir?: "+str(isdir(PREFIX+path)))
    if os.path.exists(PREFIX+path+".md"):
        with open(PREFIX+path+".md", 'r') as myfile:
            data=myfile.read()
        ptitle = data.split('\n')[0]
        s += markdown.markdown('\n'.join(data.split('\n')[1:]))
    elif os.path.exists(PREFIX+path+".html"):
        with open(PREFIX+path+".html", 'r') as myfile:
            data=myfile.read()
        ptitle = data.split('\n')[0]
        s += '\n'.join(data.split('\n')[1:])
    elif os.path.exists(PREFIX+path+".txt"):
        with open(PREFIX+path+".txt", 'r') as myfile:
            data=myfile.read()
        ptitle = data.split('\n')[0]
        s += "<pre>"+'\n'.join(data.split('\n')[1:])+"</pre>"
    elif isdir(PREFIX+path):
        if os.path.exists(PREFIX+path+"/index.md"):
            with open(PREFIX+path+"/index.md", 'r') as myfile:
                data=myfile.read()
            ptitle = data.split('\n')[0]
            s += markdown.markdown('\n'.join(data.split('\n')[1:]))
        else:
            s += "<h2>Index of "+path+"</h2>"
            s += "<ul>"
            for f in listdir(PREFIX+path):
                if os.path.exists(PREFIX+path+"/.desc"):
                    with open(PREFIX+path+"/.desc", 'r') as myfile:
                        data=myfile.read().replace('\n', '')
                    s += "<li><a href=\"/"+path+"/"+f+"\">"+f+"/</a> - "+markdown.markdown(data)+"</li>"
                else:
                    s += "<li><a href=\"/"+path+"/"+f+"\">"+f+"/</a></li>"
            s += "</ul>"
            ptitle = "Listing "+path
    elif isfile(PREFIX+path):
        return send_from_directory(directory=PREFIX+'/'.join(path.split('/')[:-1]), filename=path.split('/')[len(path.split('/'))-1])
    else:
        abort(404)
    #return navii(PREFIX+path, 0, '', True)+s+str(request.environ)
    return tmpl.format(title=ptitle, site_title=info[0], subtitle=info[1],
                       nav=navii(PREFIX+path, 0, '', True),
                       content=s, footer=info[2], topbar=info[3])

#if __name__ == '__main__':
#    app.run()
