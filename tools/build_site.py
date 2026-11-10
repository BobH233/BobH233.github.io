import html
import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / 'data/content.json').read_text())
BASE = 'https://bobh233.github.io/'
LAB_URL = 'https://lamps.bit-inin.com/'


def asset(path):
    digest = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:10]
    return f'{path}?v={digest}'


def esc(value):
    return html.escape(str(value), quote=True)


def icon(name):
    return f'<svg class="icon" aria-hidden="true"><use href="{asset("assets/icons.svg")}#{name}"></use></svg>'


def external(url, text, cls='', label=''):
    aria = f' aria-label="{esc(label)}"' if label else ''
    return f'<a class="{cls}" href="{esc(url)}" target="_blank" rel="noopener noreferrer"{aria}>{text}</a>'


def authors(value):
    return esc(value).replace('Bohan Ren', '<strong>Bohan Ren</strong>')


def image_button(item):
    return f'<button class="work-image" data-image="{esc(item["image"])}" data-image-title="{esc(item["title"])}" aria-label="Enlarge image: {esc(item["title"])}"><img src="{esc(item["image"])}" alt="{esc(item["title"])}" loading="lazy" width="900" height="506"><span class="image-expand">{icon("external-link")}</span></button>'


def work_card(item):
    paper = item['type'] == 'paper'
    label = item['venue'] if paper else item['date']
    if paper and item.get('year') and str(item['year']) not in label:
        label = f"{label} · {item['year']}"
    category = 'Publication' if paper else 'Project'
    color = 'blue' if paper else 'green'
    tag = f'<span class="tag {color}">{esc(label if paper else item["name"])}</span>'
    title = esc(item['title'])
    if item.get('url'):
        title = external(item['url'], title)
    body = f'<p class="authors">{authors(item["authors"])}</p>' if paper else f'<p class="work-description">{esc(item["description"])}</p>'
    if item.get('award'):
        body += f'<p class="award">{icon("sparkles")}{esc(item["award"])}</p>'
    if item.get('abstract'):
        body += f'<details class="abstract"><summary>Read abstract {icon("chevron-down")}</summary><p>{esc(item["abstract"])}</p></details>'
    actions = ''
    if item.get('url'):
        text = 'Paper' if paper and 'arxiv' in item['url'] else 'Project page' if not paper or 'github' in item['url'] else 'Publication'
        actions += external(item['url'], icon('file-text' if paper else 'external-link') + text, 'text-action')
    if item.get('video'):
        actions += external(item['video'], icon('player-play') + 'Video', 'text-action')
    if paper:
        citation = item['bibtex']
        actions += f'<button class="text-action" data-citation="{esc(citation)}">{icon("copy")}Cite</button>'
    actions += f'<button class="icon-button save-button" data-save="{esc(item["id"])}" aria-label="Save {esc(item["title"])}" aria-pressed="false">{icon("bookmark")}</button><button class="icon-button" data-share="{esc(item["id"])}" aria-label="Share {esc(item["title"])}">{icon("share-3")}</button>'
    featured = f'<span class="featured-label">{icon("sparkles")}Featured</span>' if item['id'] == 'cubifygs' else ''
    return f'''<article class="work-card surface" id="{esc(item['id'])}" data-kind="{item['type']}" data-work="{esc(item['id'])}">
<div class="post-byline"><img class="mini-avatar" src="images/avatar-profile.png" alt="" width="36" height="36"><div><strong>Bohan Ren</strong><span>{esc(label)} · {category}</span></div>{featured}</div>
<div class="work-copy">{tag}<h3>{title}</h3>{body}</div>{image_button(item)}<div class="post-actions">{actions}</div></article>'''


def filters(options, label):
    buttons = []
    for i, (value, text) in enumerate(options):
        buttons.append(f'<button class="filter-button {"is-active" if i == 0 else ""}" data-filter="{value}" aria-pressed="{"true" if i == 0 else "false"}">{icon("bookmark") if value == "saved" else ""}{text}</button>')
    return f'<div class="filter-list" role="group" aria-label="{label}">{"".join(buttons)}</div>'


def research():
    groups = []
    for year in [2026, 2025, 2024, None]:
        items = [p for p in DATA['publications'] + DATA['projects'] if p['year'] == year]
        if not items:
            continue
        cards = ''.join(work_card(item) for item in items)
        groups.append(f'<section class="year-group"><h2 class="year-heading"><span>{year or "Earlier work"}</span><span class="year-line"></span></h2>{cards}</section>')
    return f'''<div class="feed-tools">{filters([('all','All work'),('paper','Publications'),('project','Projects'),('saved','Saved')], 'Filter research')}<label class="search-field">{icon('search')}<input type="search" id="work-search" placeholder="Search research" aria-label="Search research" autocomplete="off"></label></div>
<div id="research-feed">{''.join(groups)}</div><div class="empty-results surface" hidden><span class="empty-icon">{icon('search')}</span><h3>No matching work</h3><p>Try another search or filter.</p><button class="button secondary" id="reset-filters">Show all work {icon('arrow-right')}</button></div>'''


def news():
    posts = []
    for post in sorted(DATA['news'], key=lambda p: p['date'], reverse=True):
        when = date.fromisoformat(post['date'])
        images = ''.join(f'<button data-image="{esc(p["src"])}" data-image-title="{esc(p["alt"])}" aria-label="Enlarge {esc(p["alt"])}"><img src="{esc(p["src"])}" alt="{esc(p["alt"])}" loading="lazy" width="{p.get("width", 600)}" height="{p.get("height", 600)}"></button>' for p in post.get('images', []))
        gallery_class = "moment-gallery mixed" if post.get("gallery_layout") == "mixed" else "moment-gallery"
        text = ''.join(f'<p>{esc(p)}</p>' for p in post['text'].split('\n') if p.strip())
        location = f'<span class="moment-location">{icon("map-pin")}{esc(post["location"])}</span>' if post.get('location') else ''
        video = next((v for v in DATA['videos'] if v['id'] == post.get('video_id')), None)
        video_preview = f'<div class="moment-video">{video_thumbnail(video)}<div class="video-copy"><h3>{esc(video["title"])}</h3>{external(video["url"], "Watch on " + video["platform"] + icon("arrow-up-right"), "text-action")}</div></div>' if video else ''
        posts.append(f'<article class="moment-card surface" id="{esc(post["id"])}"><div class="post-byline"><img class="mini-avatar" src="images/avatar-profile.png" alt="" width="36" height="36"><div><strong>Bohan Ren</strong><time datetime="{esc(post["date"])}">{when.strftime("%B")} {when.day}, {when.year}</time></div></div><div class="moment-copy">{text}</div><div class="{gallery_class}">{images}</div>{video_preview}<div class="post-actions">{location}<button class="text-action" data-share="{esc(post["id"])}">{icon("share-3")}Share</button></div></article>')
    empty = f'''<div class="moments-empty surface"><div class="photo-stack" aria-hidden="true"><div class="photo-frame frame-green">{icon('photo')}</div><div class="photo-frame frame-blue">{icon('camera')}</div><div class="photo-frame frame-yellow">{icon('sparkles')}</div></div><h3>No posts yet.</h3></div>'''
    return f'<div class="moments-feed">{"".join(posts) or empty}</div>'


def video_thumbnail(item):
    return f'''<button class="video-thumbnail" data-video="{esc(item['embed'])}" data-video-title="{esc(item['title'])}" data-video-url="{esc(item['url'])}" aria-label="Play {esc(item['title'])}"><img src="{esc(item['image'])}" alt="{esc(item['title'])} video preview" width="900" height="506" loading="lazy"><span class="play-button">{icon('player-play')}</span></button>'''


def video_card(item):
    return f'''<article class="video-card surface {'featured-video' if item.get('featured') else ''}" data-video-category="{esc(item['category'])}" id="{esc(item['id'])}">{video_thumbnail(item)}<div class="video-copy"><div class="video-meta"><span>{esc(item['category'])}</span><span>{esc(item['platform'])}</span></div><h3>{esc(item['title'])}</h3><p>{esc(item['description'])}</p>{external(item['url'], 'Watch on ' + item['platform'] + icon('arrow-up-right'), 'text-action')}</div></article>'''


def videos():
    return f'''<div class="feed-tools">{filters([('all','All videos'),('Mapping','Mapping'),('Robotics','Robotics'),('Interaction','Interaction'),('Conferences','Conferences'),('Campus life','Campus life')], 'Filter videos')}</div><div class="video-grid">{''.join(video_card(item) for item in DATA['videos'])}</div>'''


def about():
    return f'''<section class="about-card surface" id="about"><h3>Hi, it’s me!</h3><p>I'm a second-year master's student in Control Science and Engineering at the School of Automation, Beijing Institute of Technology, and a member of the {external(LAB_URL, "Integrated Navigation and Intelligent Navigation (ININ) Laboratory", "lab-link")}.</p><p>My previous research focused on 3D Gaussian Splatting SLAM, scene reconstruction, and lifelong scene maintenance in dynamic environments.</p><p>I'm currently learning about Vision-Language-Action (VLA) models and generative methods, especially Flow Matching. My goal is to build robotic technology that people can use and benefit from in everyday life.</p><div class="about-contact-links"><a class="button primary" href="mailto:renbohan@bit.edu.cn">{icon('mail')}Say hello {icon('arrow-up-right')}</a>{external('https://scholar.google.com/citations?user=N5gglbwAAAAJ', icon('school') + 'Google Scholar', 'button secondary')}</div></section>
<section class="about-section surface" id="research"><h3>{icon('sparkles')}What I'm exploring</h3><div class="interest-row"><span class="interest-icon blue">{icon('robot-arm')}</span><div><h4>Vision-Language-Action</h4><p>Learning how vision and language guide embodied action.</p><span class="small-label">Currently learning</span></div></div><div class="interest-row"><span class="interest-icon green flow-matching-icon">{icon('flow-matching')}</span><div><h4>Flow Matching</h4><p>Exploring generative models and continuous flows.</p><span class="small-label">Currently learning</span></div></div><div class="interest-row"><span class="interest-icon yellow">{icon('reconstruction')}</span><div><h4>3D Gaussian Splatting & SLAM</h4><p>Mapping, reconstruction, and lifelong dynamic scene maintenance.</p><span class="small-label">Previous research</span></div></div></section>
<section class="about-section surface"><h3>{icon('school')}Education & lab</h3><div class="education-item"><img class="education-mark" src="images/bit-logo.png" alt="北京理工大学校徽" width="43" height="43"><div><h4>Beijing Institute of Technology</h4><p>2025–now</p><p>Master's student · Year 2<br>Control Science and Engineering<br>School of Automation</p>{external(LAB_URL, "组合导航与智能导航实验室 · ININ", "tag green lab-link")}</div></div><div class="education-item"><img class="education-mark" src="images/bit-logo.png" alt="北京理工大学校徽" width="43" height="43"><div><h4>Beijing Institute of Technology</h4><p>2021–2025</p><p>Bachelor's degree<br>Automation<br>XUTELI School · 徐特立学院</p></div></div></section>'''


def friends():
    cards = []
    for friend in DATA['friends']:
        affiliation = f'<p>{esc(friend["affiliation"])}</p>' if friend.get('affiliation') else ''
        content = f'<img class="friend-avatar" src="{esc(friend["image"])}" alt="" width="72" height="72"><div class="friend-details"><h2>{esc(friend["name"])}</h2><span class="friend-handle">{esc(friend["handle"])}</span>{affiliation}</div>{icon("arrow-up-right")}'
        cards.append(external(friend['url'], content, 'friend-card surface', f"Visit {friend['name']}’s homepage"))
    return f'<div class="friends-grid" aria-label="Friends">{"".join(cards)}</div>'


def sidebar():
    return f'''<aside class="profile-sidebar" aria-label="Profile introduction"><section class="intro-card surface"><div class="card-heading"><h2>A little about me</h2>{icon('sparkles')}</div><ul class="profile-facts"><li>{icon('school')}<span>Beijing Institute of Technology<br><small>School of Automation · Year 2</small></span></li><li>{icon('navigation')}{external(LAB_URL, "ININ Laboratory<br><small>组合导航与智能导航实验室</small>", "lab-link")}</li><li>{icon('map-pin')}<span>Beijing, China</span></li></ul><a class="sidebar-about" href="about.html">More about me {icon('arrow-up-right')}</a></section><section class="links-card surface"><h2>Find me elsewhere</h2>{external('https://scholar.google.com/citations?user=N5gglbwAAAAJ',f'<span class="link-icon blue">{icon("school")}</span><span>Google Scholar</span>{icon("arrow-up-right")}', 'profile-link')}{external('https://github.com/BobH233',f'<span class="link-icon green">{icon("brand-github")}</span><span>GitHub</span>{icon("arrow-up-right")}', 'profile-link')}<a class="profile-link" href="mailto:renbohan@bit.edu.cn"><span class="link-icon yellow">{icon('mail')}</span><span>Email</span>{icon('arrow-up-right')}</a></section></aside>'''


def right_sidebar():
    return f'''<aside class="notes-sidebar" aria-label="Research interests"><section class="learning-card"><div class="card-heading"><h2>On my mind</h2>{icon('book-2')}</div><span class="learning-label">Currently learning</span><a class="learning-topic" href="about.html#research"><span class="topic-number">01</span><div><h3>VLA</h3><p>Vision · Language · Action</p></div>{icon('arrow-up-right')}</a><a class="learning-topic" href="about.html#research"><span class="topic-number">02</span><div><h3>Flow Matching</h3><p>Generative models</p></div>{icon('arrow-up-right')}</a></section><footer class="site-footer">© 2026 Bohan Ren</footer></aside>'''


def cover():
    return f'''<section class="profile-header" aria-label="Bohan Ren's profile"><div class="profile-cover"><div class="cover-copy"><p>Robotics for<br><span>everyday life.</span></p></div><div class="cover-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="cover-sun">✳</div><div class="research-tile tile-vision">{icon('stack-2')}<span>perception</span></div><div class="research-tile tile-action">{icon('robot')}<span>action</span></div><span class="orbit-star">+</span></div></div><div class="profile-identity"><img class="profile-avatar" src="images/avatar-profile.png" alt="Bohan Ren" width="144" height="144" fetchpriority="high"><div class="identity-copy"><div class="name-line"><h1>Bohan Ren</h1><span class="name-pronunciation">@BobH233</span></div><p>Second-year master's student <span>·</span> {external(LAB_URL, "ININ Lab", "lab-link")}, BIT</p></div><a class="button primary contact-button" href="mailto:renbohan@bit.edu.cn">{icon('mail')}Get in touch {icon('arrow-up-right')}</a></div>'''


def page(key, filename, title, description, content):
    navs = [('research','index.html','school','Research',str(len(DATA['publications']) + len(DATA['projects']))),('news','news.html','news','News',''),('videos','videos.html','movie','Videos',str(len(DATA['videos']))),('about','about.html','user-circle','About',''),('friends','friends.html','users','Friends','')]
    tabs = ''.join(f'<a class="profile-tab {"is-active" if k == key else ""}" href="{url}" {"aria-current=page" if k == key else ""}>{icon(ic)}{label}{f"<span>{count}</span>" if count else ""}</a>' for k,url,ic,label,count in navs)
    canonical = BASE + ('' if filename=='index.html' else filename)
    schema = {'@context':'https://schema.org','@type':'Person','name':'Bohan Ren','url':BASE,'image':BASE+'images/avatar-profile.png','affiliation':{'@type':'CollegeOrUniversity','name':'Beijing Institute of Technology'},'memberOf':{'@type':'Organization','name':'Integrated Navigation and Intelligent Navigation (ININ) Laboratory','url':LAB_URL},'jobTitle':"Second-year Master's Student",'sameAs':['https://github.com/BobH233','https://scholar.google.com/citations?user=N5gglbwAAAAJ']}
    return f'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#f5f8f6">
<link rel="canonical" href="{canonical}"><link rel="icon" type="image/png" href="images/avatar-profile.png"><link rel="stylesheet" href="{asset('style.css')}"><link rel="preload" href="assets/fonts/nunito-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<meta property="og:type" content="website"><meta property="og:site_name" content="Bohan Ren"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}images/avatar-profile.png">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{BASE}images/avatar-profile.png">
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script><script src="{asset('script.js')}" defer></script></head>
<body data-page="{key}"><a class="skip-link" href="#main-content">Skip to content</a>
<div class="site-container">{cover()}<nav class="profile-tabs" aria-label="Profile pages">{tabs}</nav></section><div class="page-grid">{sidebar()}<main id="main-content" tabindex="-1">{content}</main>{right_sidebar()}</div></div>
<dialog id="content-dialog" aria-labelledby="dialog-title"><div class="dialog-header"><h2 id="dialog-title"></h2><button class="icon-button" id="close-dialog" aria-label="Close dialog">{icon('x')}</button></div><div id="dialog-content"></div></dialog><div class="toast" id="toast" role="status" aria-live="polite"></div>
</body></html>'''


def main():
    sprites = []
    for file in sorted((ROOT/'assets/icons').glob('*.svg')):
        svg = re.search(r'<svg\b([^>]*)>(.*?)</svg>', file.read_text(), re.S)
        view_box = re.search(r'viewBox="([^"]+)"', svg.group(1)).group(1)
        sprites.append(f'<symbol id="{file.stem}" viewBox="{esc(view_box)}">{svg.group(2)}</symbol>')
    (ROOT/'assets/icons.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg">'+''.join(sprites)+'</svg>\n')
    pages = [('research','index.html','Bohan Ren | Robotics, Vision & Research',"Bohan Ren, second-year master's student at BIT's ININ Laboratory. Research in 3DGS-SLAM, with growing interests in VLA and Flow Matching.",research()),('news','news.html','News & Moments | Bohan Ren','Conferences, lab life, and little discoveries from Bohan Ren at Beijing Institute of Technology.',news()),('videos','videos.html','Research Videos | Bohan Ren','Research demos, autonomous racing, conference trips, and a Cambridge exchange vlog by Bohan Ren.',videos()),('about','about.html','About | Bohan Ren',"Meet Bohan Ren, a second-year master's student in Control Science and Engineering at Beijing Institute of Technology's ININ Laboratory.",about()),('friends','friends.html','Friends | Bohan Ren',"Friends of Bohan Ren and their personal homepages.",friends())]
    for key,filename,title,description,content in pages:
        (ROOT/filename).write_text(page(key,filename,title,description,content))
    print(f'Built {len(pages)} pages from data/content.json.')


if __name__ == '__main__':
    main()
