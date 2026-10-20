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
c.box(xs[2],210,w,130,'Receiver and queue',['Validate and enqueue','FIFO or strict priority'])
c.box(xs[3],210,w,130,'Single worker',['20 ms synthetic service','JSON latency output'])
for a,b in zip(xs,xs[1:]):c.arrow([(a+w,275),(b,275)])
c.text(60,365,'Demo queue: 10,000 events. Invalid input / full queue is logged. Live validation pending.',19,MUTED)
c.text(60,440,'REPRODUCIBLE EXPERIMENT',20,TEAL,True)
c.box(xs[0],490,w,145,'Seeded workload',['Poisson arrivals','Same trace per policy'],TEAL)
c.box(xs[1],490,w,145,'Simulation runner',['FIFO / strict priority','Fixed aging (pilot)'],TEAL)
c.box(xs[2],490,w,145,'Per-event evidence',['Arrival, start, finish','Waiting and latency'],TEAL)
c.box(xs[3],490,w,145,'Analysis and report',['CSV + config + hashes','Paired pilot intervals'],TEAL)
for a,b in zip(xs,xs[1:]):c.arrow([(a+w,560),(b,560)],TEAL)
c.text(60,660,'Simulation: modeled time, one worker; optional bounded queue; no broker dependency.',19,MUTED)
c.box(60,735,1320,130,'Planned research extensions',['Aggregate deadline and loss metrics  |  EDF baseline', 'Congestion-aware aging candidate  |  Controlled MQTT evaluation'],GRAY,True)
c.text(60,900,'Blue / green: implemented components. Gray: planned work.',20,MUTED)
c.text(60,935,'The application queue is after MQTT delivery; this design makes no network timing guarantee.',19,MUTED)
c.save('high-level-architecture')

c=Canvas(1200,1300)
c.text(60,90,'Current live MQTT demo; non-preemptive processing',22,MUTED)
x=310;w=560
c.box(x,150,w,100,'Receive message',['Callback receives payload from lab/alerts'])
c.arrow([(590,250),(590,285)])
c.box(x,285,w,105,'Validate payload',['String event ID and priority 0, 1 or 2'])
c.arrow([(870,337),(1010,337),(1010,440)])
c.text(940,300,'Invalid',18,MUTED)
c.box(895,440,260,120,'Reject and log',['Invalid payload','or full queue'],GRAY)
c.arrow([(590,390),(590,445)])
c.text(610,406,'Valid',18,MUTED)
c.box(x,445,w,105,'Attempt queue admission',['Bounded queue: 10,000 waiting events'])
c.arrow([(870,497),(895,497)])
c.text(883,575,'Full',18,MUTED)
c.arrow([(590,550),(590,610)])
c.text(610,568,'Admitted',18,MUTED)
c.box(x,610,w,120,'Select next waiting alert',['FIFO: receiver arrival order','Priority: highest urgency; arrival breaks ties'])
c.arrow([(590,730),(590,785)])
c.box(x,785,w,100,'Process one alert',['20 ms synthetic service; no preemption'])
c.arrow([(590,885),(590,940)])
c.box(x,940,w,100,'Emit result',['JSON event and receiver-local latency'])
c.arrow([(310,990),(180,990),(180,670),(310,670)])
c.text(65,805,'Next alert',18,MUTED)
c.text(65,834,'Wait if empty',18,MUTED)
c.box(60,1110,1080,105,'Planned research flow additions',['Deduplication, trusted deadline metadata and complete admission metrics'],GRAY,True)
c.text(60,1240,'Fixed aging runs in the separate simulation pilot; it is not part of this live demo.',18,MUTED)
c.save('alert-processing-flow')
