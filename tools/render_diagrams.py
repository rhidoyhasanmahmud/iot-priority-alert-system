"""Render README diagrams as PNG and editable SVG. Requires Pillow."""
from pathlib import Path
from html import escape
import math
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parents[1]/'docs/images'
OUT.mkdir(parents=True,exist_ok=True)
INK='#172B4D';MUTED='#526580';BLUE='#2563EB';TEAL='#087F8C';GRAY='#718096'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
class Canvas:
 def __init__(self,w,h):
  self.im=Image.new('RGB',(w,h),'white');self.d=ImageDraw.Draw(self.im)
  self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>']
 def text(self,x,y,s,size=22,color=INK,bold=False,center=False):
  font=ImageFont.truetype(BOLD if bold else FONT,size)
  self.d.text((x,y),s,font=font,fill=color,anchor='mt' if center else 'lt')
  anchor='middle' if center else 'start'
  self.svg.append(f'<text x="{x}" y="{y+size*.85}" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')
 def box(self,x,y,w,h,title,lines=(),color=BLUE,planned=False):
  fill='#F1F5F9' if planned else '#EFF6FF' if color==BLUE else '#ECFDF5'
  self.d.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=fill,outline=color,width=2)
  self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{color}" stroke-width="2"'+(' stroke-dasharray="8 5"' if planned else '')+'/>')
  self.text(x+w/2,y+20,title,22,color,True,True)
  for i,line in enumerate(lines):self.text(x+w/2,y+55+i*28,line,18,MUTED,center=True)
 def arrow(self,pts,color=GRAY):
  self.d.line(pts,fill=color,width=3)
  self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
  x,y=pts[-1];a,b=pts[-2];angle=math.atan2(y-b,x-a)
  tri=[(x,y),(x-12*math.cos(angle-.45),y-12*math.sin(angle-.45)),(x-12*math.cos(angle+.45),y-12*math.sin(angle+.45))]
  self.d.polygon(tri,fill=color);self.svg.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in tri)+f'" fill="{color}"/>')
 def save(self,name):
  # README headings supply the titles; trim the unused top margin in both formats.
  width,height=self.im.size
  self.im.crop((0,60,width,height)).save(OUT/(name+'.png'))
  self.svg[1]=f'<rect x="0" y="60" width="{width}" height="{height-60}" fill="white"/>'
  self.svg[0]=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height-60}" viewBox="0 60 {width} {height-60}">'
  (OUT/(name+'.svg')).write_text('\n'.join(self.svg+['</svg>'])+'\n')

c=Canvas(1440,1010)
c.text(60,91,'Two execution paths: live demonstration and reproducible simulation',22,MUTED)
c.text(60,160,'LIVE MQTT DEMO',20,BLUE,True)
xs=[60,405,750,1095];w=285
c.box(xs[0],210,w,130,'Event publisher',['Synthetic alerts','MQTT QoS 1'])
c.box(xs[1],210,w,130,'Mosquitto broker',['Topic: lab/alerts','Localhost port 1883'])
c.box(xs[2],210,w,130,'Receiver and queue',['Validate + deduplicate','8 scheduling policies'])
c.box(xs[3],210,w,130,'Single worker',['20 ms synthetic service','CSV + local latency'])
for a,b in zip(xs,xs[1:]):c.arrow([(a+w,275),(b,275)])
c.text(60,365,'Bounded queue + TTL dedup; JSON receipts, CSV completions and summary. Controlled evaluation pending.',19,MUTED)
c.text(60,440,'REPRODUCIBLE EXPERIMENT',20,TEAL,True)
c.box(xs[0],490,w,145,'Seeded workload',['Normal / burst + replay','Same trace per policy'],TEAL)
c.box(xs[1],490,w,145,'Simulation runner',['8 shared selector policies','Baseline + guarded aging'],TEAL)
c.box(xs[2],490,w,145,'Per-event evidence',['Arrival, start, finish','Waiting and latency'],TEAL)
c.box(xs[3],490,w,145,'Analysis and report',['Registered tuning / evaluation','Paired intervals + plots'],TEAL)
for a,b in zip(xs,xs[1:]):c.arrow([(a+w,560),(b,560)],TEAL)
c.text(60,660,'Simulation: modeled time, one worker; optional bounded queue; no broker dependency.',19,MUTED)
c.box(60,735,1320,130,'Remaining validation',['Controlled MQTT experiments  |  Reconnect and overload stress', 'Full primary experiments  |  Evidence review and release'],GRAY,True)
c.text(60,900,'Blue / green: implemented components. Gray: planned work.',20,MUTED)
c.text(60,935,'The application queue is after MQTT delivery; this design makes no network timing guarantee.',19,MUTED)
c.save('high-level-architecture')

c=Canvas(1200,1520)
c.text(60,90,'Live MQTT path; one non-preemptive worker',22,MUTED)
x=310;w=560
c.box(x,150,w,100,'Receive message',['Callback timestamp from monotonic clock'])
c.arrow([(590,250),(590,285)])
c.box(x,285,w,105,'Validate payload',['Source + ID, priority and optional deadline'])
c.arrow([(870,337),(1025,337),(1025,440)])
c.text(935,300,'Invalid',18,MUTED)
c.box(895,440,260,120,'Record receipt',['Invalid / full / conflict','Duplicate suppressed'],TEAL)
c.arrow([(590,390),(590,445)])
c.box(x,445,w,105,'Check source + event ID',['Pinned pending IDs + bounded completion TTL'])
c.arrow([(870,497),(895,497)])
c.arrow([(590,550),(590,610)])
c.text(610,568,'New identity',18,MUTED)
c.box(x,610,w,105,'Attempt queue admission',['Waiting slots exclude the active worker'])
c.arrow([(870,662),(1025,662),(1025,560)])
c.text(1040,605,'Full',18,MUTED)
c.arrow([(590,715),(590,775)])
c.text(610,733,'Admitted',18,MUTED)
c.box(x,775,w,120,'Select next alert',['FIFO / priority / fixed aging / EDF','Adaptive and matched variants share selector'])
c.arrow([(590,895),(590,950)])
c.box(x,950,w,100,'Process one alert',['Configured synthetic service; no preemption'])
c.arrow([(590,1050),(590,1105)])
c.box(x,1105,w,100,'Record completion',['Waiting, service, latency and deadline status'])
c.arrow([(310,1155),(180,1155),(180,835),(310,835)])
c.text(65,970,'Next alert',18,MUTED)
c.text(65,999,'Wait if empty',18,MUTED)
c.box(60,1280,1080,105,'Output and shutdown',['JSON receipts + CSV completions; completed ID cache uses TTL', 'Disconnect intake, drain admitted alerts; cache resets on restart'],TEAL)
c.text(60,1420,'Real callback / worker interleaving differs from simulated arrival batches.',18,MUTED)
c.save('alert-processing-flow')
