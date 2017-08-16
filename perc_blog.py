import datetime
import os
import markdown
import sys

def isint(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def isblogfile(s):
    return s.endswith(".md") and isint(s[:-3])

def validdate(y,m,d):
    try:
        n = datetime.datetime(y,m,d)
    except ValueError:
        return False
    return n

def isblogdir(s, t):
    if t=='y':
        return isint(s) and len(s)==4
    if t=='m':
        return isint(s) and int(s) > 0 and int(s) <= 12
    if t=='d':
        return isint(s) and int(s) > 0 and int(s) <= 32
    return False

def new_post(title):
    t = datetime.date.today()
    l = "blog/"+str(t.year)+"/"+str(t.month)+"/"+str(t.day)
    if not os.path.exists(l):
        os.makedirs(l)
    maxid = 0
    nextid = 0
    for i in os.listdir(l):
        if i.endswith(".md"):
            try:
                n = int(i[:-3])
                if n > maxid:
                    maxid=n
            except ValueError:
                pass
    nextid = maxid+1
    with open(l+"/"+str(nextid)+".md", 'w') as f:
        f.write(title+"\n#"+title+"\n")
    print("File "+l+"/"+str(nextid)+".md created, edit it as you please.")

def get_posts():
    p = []
    for i in [x for x in os.listdir("blog") if isblogdir(x, 'y')]:
        for j in [x for x in os.listdir("blog/"+i) if isblogdir(x, 'm')]:
            for k in [x for x in os.listdir("blog/"+i+"/"+j) if isblogdir(x, 'd')]:
                g = validdate(int(i), int(j), int(k))
                if g:
                    for l in [x for x in os.listdir("blog/"+i+"/"+j+"/"+k) if isblogfile(x)]:
                        if os.path.isfile('blog/'+i+'/'+j+'/'+k+'/'+l):
                            p.append({'date':g,
                                      'file':'blog/'+i+'/'+j+'/'+k+'/'+l})
    return sorted(p, key=lambda k: k['date'])[::-1]

def update():
    s = ""
    e = 0
    s += "Blog index\n"
    for post in get_posts():
        g = []
        with open(post['file'], 'r') as l:
            for line in l:
                g.append(line)
        s += "<div class=\"blogpost\">"
        s += "<h1><a href=\"/"+post['file'][:-3]+"\">"+g[0][:-1]+"</a> ("+post['date'].strftime('%Y-%m-%d')+")</h1>"
        if g[1].startswith('#'):
            s += markdown.markdown(''.join(g[2:]))
        else:
            s += markdown.markdown(''.join(g[1:]))
        s += "</div>"
        e += 1
    with open("blog/index.md", 'w') as f:
        f.write(s)
    print(str(e)+ " posts read, blog/index.md made.")


if sys.argv[1] == "new":
    if len(sys.argv) > 2:
        new_post(' '.join(sys.argv[2:]))
    else:
        new_post("Post title here")
    update()
elif sys.argv[1] == "update":
    update()
