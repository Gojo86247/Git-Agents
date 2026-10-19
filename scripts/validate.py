from pathlib import Path
import ast,json,re,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
S=R/'skills'
expected={'scenario-lab','feature-lens','youtube-studio','instagram-studio'}
assert {p.name for p in S.iterdir() if p.is_dir()}==expected
for name in expected:
    p=S/name/'SKILL.md'; text=p.read_text()
    assert text.startswith('---\n') and f'name: {name}\n' in text and 'description:' in text
    assert (S/name/'agents/openai.yaml').exists()
    for link in re.findall(r'\]\(([^)]+)\)',text):
        if '://' not in link and not link.startswith('#'): assert (p.parent/link).exists(),link
for p in S.rglob('*.py'): ast.parse(p.read_text(),filename=str(p))
for p in S.rglob('*.json'): json.loads(p.read_text())
with tempfile.TemporaryDirectory() as d:
    d=Path(d)
    (d/'text.txt').write_text('I tested three ways to organize my desk.\nHere is the simplest method.\nKeep one tray for unfinished work.\nTry it on your desk today.\n')
    (d/'captions.srt').write_text(''.join(f'{i+1}\n00:{i*8//60:02}:{i*8%60:02},000 --> 00:{(i*8+6)//60:02}:{(i*8+6)%60:02},000\n' + ['Organize the desk surface first.','Choose a tray for paper mail.','Review the system each week.'][i//4]+'\n\n' for i in range(12)))
    (d/'retention.csv').write_text('seconds,retention\n'+''.join(f'{i*5},{100-i*5}\n' for i in range(10)))
    (d/'videos.json').write_text(json.dumps([{'channel':'Example','title':'I tested three methods','views':v} for v in (100,120,130,1000)]))
    (d/'reels.tsv').write_text('account\tfollowers\tmedian\tviews\thook\n@example\t1000\t100\t1000\tI tested three methods\n')
    jobs=[
      ('youtube-studio','yt-script/hookscore.py',['--hook','I tested three ways to organize my desk','--json']),
      ('youtube-studio','yt-package/title.py',['--title','Three ways to organize your desk','--thumb','One clear surface','--json']),
      ('youtube-studio','yt-edit/deadair.py',[str(d/'captions.srt'),'--json']),
      ('youtube-studio','yt-chapters/chapters.py',[str(d/'captions.srt'),'--json']),
      ('youtube-studio','yt-retention/retention.py',[str(d/'retention.csv'),'--axis','seconds','--json']),
      ('youtube-studio','yt-viral/swipe.py',[str(d/'videos.json'),'--json']),
      ('instagram-studio','ig-reel/hookscore.py',['--hook','I tested three ways to organize my desk','--json']),
      ('instagram-studio','ig-reel/beats.py',[str(d/'text.txt'),'--target','30','--json']),
      ('instagram-studio','ig-caption/caption.py',[str(d/'text.txt'),'--json']),
      ('instagram-studio','ig-human/humanize.py',[str(d/'text.txt'),'--json']),
      ('instagram-studio','ig-human/detect.py',[str(d/'text.txt'),'--json']),
      ('instagram-studio','ig-viral/swipe.py',[str(d/'reels.tsv'),'--json'])]
    for name,rel,args in jobs:
        p=S/name/'references'/rel
        x=subprocess.run([sys.executable,str(p),*args],capture_output=True,text=True,timeout=20)
        assert x.returncode in ((0,1) if rel in ("ig-caption/caption.py","ig-human/detect.py") else (0,)),(rel,x.stderr,x.stdout)
        obj=json.loads(x.stdout); assert obj is not None
        if rel=='yt-package/title.py': assert obj[0]['title']=='Three ways to organize your desk'
        if rel=='yt-chapters/chapters.py': assert obj['chapters'][0]['start']==0
        print('PASS',rel)
    p=S/'youtube-studio/references/yt-retention/retention.py'
    x=subprocess.run([sys.executable,str(p),str(d/'retention.csv')],capture_output=True,text=True)
    assert x.returncode!=0 and 'axis' in x.stderr
print('PASS four skill manifests, links, data files, 12 utility executions and explicit-axis guard')
