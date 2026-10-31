"""Conservative native OCC distance proof for rigid translations."""
import sys
sys.path.insert(0,"/Applications/FreeCAD.app/Contents/Resources/lib")
import FreeCAD,Part
V=FreeCAD.Vector
import math
_boxes={}
_slabs={}
# Cache keys are Python wrapper IDs, not durable CAD identities. Retain
# EVERY cached wrapper for the process lifetime: otherwise a temporary
# ob.Shape or s.copy() can die and its ID can be reused for another shape,
# incorrectly returning an unrelated box/slab. Native shapes remain native;
# this is lifetime bookkeeping, not geometric approximation or healing.
_shape_refs={}
def register_outer_profile_boxes(s,name):
 """Exact source-primitive supersets for subtractively machined parts.

 H05outerYZpolygon is preserved in overhead_r3.commands.json; holes only
 subtractmaterial. G15R4/R5 are nativeunionsofthese3boxes, then cuts.
 No vendor/latch mesh approximations or shape-filling Boolean edits.
 """
 _shape_refs[id(s)]=s
 if name.startswith('H05_OVERHEAD_WEB_'):
  lo,hi=bbox(s);assert abs(lo[2]+20)<1e-5 and abs(hi[2]-90)<1e-5
  rows=[]
  for z in range(-20,80,5):
   top=z+5;mn=75-top/4;mx=96.095 if z<=65 else 96.095-(z-65)*21.095/25
   rows.append([[lo[0],mn,z],[hi[0],mx,top]])
  for z in [80,85]:rows.append([[lo[0],20,z],[hi[0],96.095-(z-65)*21.095/25,z+5]])
  _slabs[id(s)]=rows
 elif name.startswith('G15_')and name.endswith(('R4','R5')):
  rows=[[[200,-75,-12.7],[240,-5,0]],[[240,-26,-12.7],[324,-5,0]],[[305.25,-19.5,-12.7],[344,55,0]]]
  if '_L_'in name:rows=[[[-hi[0],lo[1],lo[2]],[-lo[0],hi[1],hi[2]]]for lo,hi in rows]
  _slabs[id(s)]=rows
def bbox(s):
 # BRep BoundBox may enclose remote NURBS control poles, not just surfaces.
 # Native AddOptimal without triangulation, including shape tolerances.
 key=id(s)
 _shape_refs[key]=s
 if key not in _boxes:
  b=s.optimalBoundingBox(False,True)
  _boxes[key]=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
 return _boxes[key]
def slab_boxes(s,height=5):
 key=id(s)
 _shape_refs[key]=s
 if key not in _slabs:
  lo,hi=bbox(s);rows=[];total=0;z=lo[2]
  while z<hi[2]-1e-7:
   end=min(z+height,hi[2]);clip=Part.makeBox(hi[0]-lo[0]+2,hi[1]-lo[1]+2,end-z+.002,V(lo[0]-1,lo[1]-1,z-.001))
   cut=s.common(clip)
   if not cut.isNull():
    #Do not cache temporaryShape byid: itsPythonid can be reused.
    b=cut.optimalBoundingBox(False,True);rows.append([[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]])
    total+=cut.Volume
   z=end
  if s.Volume>1e-6 and total<s.Volume-max(.01,s.Volume*1e-5):raise ValueError('Zslab partition lost source volume')
  _slabs[key]=rows
 return _slabs[key]
def certify_with_slabs(a,b,axes,intervals,clearance=.1,budget=3000):
 #Native exactintersection with overlappingZslabs yields conservativeboxes
 #coveringthewhole moving body. All boxes must clear the full swept domain.
 aa=bbox(a);bb=bbox(b);swept=[aa[0][:],aa[1][:]]
 for ax,(lo,hi)in zip(axes,intervals):swept[0][ax]+=lo;swept[1][ax]+=hi
 if box_distance(swept,bb)>clearance+1e-6:return certify(a,b,axes,intervals,clearance,budget)
 bound=float('inf');ok=True
 try:
  boxes=slab_boxes(a)
  for aa in boxes:
   swept=[aa[0][:],aa[1][:]]
   for ax,(lo,hi)in zip(axes,intervals):swept[0][ax]+=lo;swept[1][ax]+=hi
   v=box_distance(swept,bb);bound=min(bound,v)
   if v<=clearance+1e-6:ok=False;break
  if ok:return {'certified':True,'kind':'SOURCE_PRIMITIVE_OR_NATIVE_Z_SLAB_SWEEP_BOUND','certified_lower_bound_mm':bound,
   'native_partition_slabs':len(boxes),'cells':len(boxes),'distance_calls':0}
 except Exception:pass
 return certify(a,b,axes,intervals,clearance,budget)
def box_distance(a,b):return math.sqrt(sum(max(b[0][i]-a[1][i],a[0][i]-b[1][i],0)**2 for i in range(3)))
def certify(a,b,axes,intervals,clearance=.1,budget=3000):
 aa=bbox(a);bb=bbox(b);queue=[intervals];calls=0;cells=0;minimum=float('inf');bound=float('inf')
 while queue:
  cell=queue.pop();cells+=1;swept=[aa[0][:],aa[1][:]]
  for ax,(lo,hi)in zip(axes,cell):swept[0][ax]+=lo;swept[1][ax]+=hi
  lower=box_distance(swept,bb)
  if lower>clearance+1e-6:bound=min(bound,lower);continue
  shift=[0,0,0]
  for ax,(lo,hi)in zip(axes,cell):shift[ax]=(lo+hi)/2
  s=a.copy();s.translate(V(*shift));distance=s.distToShape(b)[0];calls+=1;minimum=min(minimum,distance)
  radius=math.sqrt(sum(((hi-lo)/2)**2 for lo,hi in cell));lower=distance-radius
  if lower>clearance+1e-6:bound=min(bound,lower);continue
  if distance<=clearance+1e-6:
   return {'certified':False,'kind':'NEAR_OR_COLLISION','distance_mm':distance,'volume_mm3':s.common(b).Volume,'pose':shift,'cells':cells,'distance_calls':calls}
  if cells>=budget or radius<1e-5:return {'certified':False,'kind':'UNRESOLVED_BUDGET_OR_RESOLUTION','cells':cells,'distance_calls':calls,'remaining':len(queue)+1}
  dim=max(range(len(cell)),key=lambda i:cell[i][1]-cell[i][0]);lo,hi=cell[dim];mid=(lo+hi)/2
  left=list(cell);right=list(cell);left[dim]=(lo,mid);right[dim]=(mid,hi);queue.extend([left,right])
 return {'certified':True,'kind':'CONTINUOUS_TRANSLATION_BOUND','certified_lower_bound_mm':bound,
 'min_sampled_distance_mm':None if minimum==float('inf')else minimum,'cells':cells,'distance_calls':calls}
