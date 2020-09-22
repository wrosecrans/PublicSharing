
from lxml import etree
import copy
import random

verbose = False

# Label colors exposed by Premiere UI by default.
label_colors = ["Violet", "Iris", "Caribbean", "Lavender", "Cerulean", "Forest", "Rose", "Mango", "Purple", "Blue", "Teal", "Magenta", "Tan", "Green", "Brown", "Yellow"]

                        
def put_in_bin(bin, child):
    ### Put Child sequence into a Bin object.  (XML bin.append(child) doesn't work.)
    children = bin.find('./children')
    children.append(child)     
                        
def make_bin(name, parent=None, label="Mango", children=[]):
    ### Valid label names in default Premiere in label_colors.  Can also be "random"
    if label == "random":
      label = random.choice(label_colors)
    if parent is not None:
      bin = etree.SubElement(parent, "bin")
    else:
      bin = etree.Element("bin")
    n = etree.SubElement(bin, "name")
    n.text = name
    
    # Premiere considers a labels with only a label2 but no label1 to be correct
    # Don't blame me.  I don't make the rules.
    l = etree.SubElement(bin, "labels")
    l2 = etree.SubElement(l, "label2")
    l2.text = label
    
    c = etree.SubElement(bin, "children")
    for child in children:
      c.append(child)
    return bin
                        
def set_seq_audio_fmt(seq):
  ### Give a sequence some sane-default stereo audio.
  
  # Yes, I need to extend this to work with more than just a test file I had laying around.
  # That said, the sequence audio format doesn't need to match the audio format of the files.
  
  ch = "<numOutputChannels>2</numOutputChannels>"
  fmt = "<format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format>"
  outputs = """ <outputs> <group>
        <index>1</index>
        <numchannels>1</numchannels>
        <downmix>0</downmix>
        <channel> <index>1</index> </channel> </group>
    <group>
        <index>2</index>
        <numchannels>1</numchannels>
        <downmix>0</downmix>
        <channel> <index>2</index> </channel> </group> </outputs>
        """
  
def xml_video_format(context = "sequence"):
    ### Set context to "sequence" or "clip" because the schemas are almost but not quite identical.
    fmt_string = """
    <samplecharacteristics>
        <rate>
            <timebase>24</timebase>
            <ntsc>TRUE</ntsc>
        </rate>
        <width>1920</width>
        <height>1080</height>
        <anamorphic>FALSE</anamorphic>
        <pixelaspectratio>square</pixelaspectratio>
        <fielddominance>none</fielddominance>
        <colordepth>24</colordepth>
    </samplecharacteristics> """
    if context == "sequence":
        return etree.fromstring("<format>" + fmt_string + "</format>")
    elif context == "clip":
        return etree.fromstring("fmt_string")
    else:
        raise TypeError("xml_video_format requested with an unknown context: " + repr(context) + " (should be sequence or clip.)")

def get_or_create(node, name, clear = False):
    ### Create a child of node if it doesn't exist, or get the existing one with that name.  Optionally, clear it if it exists.
    newnode = node.find(name)
    if newnode is None:
      newnode = etree.SubElement(node, name)
    elif clear:
      newnode.clear()
    return newnode
      
      
def logginginfo(node, description="", scene="", shottake="", lognote=""):

    info = get_or_create(node, "logginginfo")
    
    dn = get_or_create(info, "description")
    if description != "":
      dn.text = description
      
    sn = get_or_create(info, "scene")
    if scene != "":
      sn.text = scene
      
    tn = get_or_create(info, "shottake")
    if shottake != "":
      tn.text = shottake
      
    ln = get_or_create(info, "lognote")
    if lognote != "":
      ln.text = lognote
      
    return info



def lognotes_for_file(node, shotdb):
  lognote = shotdb['notes']
  scene = shotdb['shot'] + ': ' + shotdb['day']
  shottake = shotdb['take']
  description = shotdb['angle'] + ' / ' + shotdb['chars'] + '   (' + shotdb['good'] + ')'
  return (node, description, scene, shottake, lognote)


def copy_timing(src, dst):
  start = copy.copy(src.find('start')) # <start>0</start>
  end = copy.copy(src.find('end'))     # <end>120</end>
  in_pt = copy.copy(src.find('in'))    # <in>0</in>
  out = copy.copy(src.find('out'))     # <out>120</out>
  duration = copy.copy(src.find('duration'))
  
  dst.append(start)
  dst.append(end)
  dst.append(in_pt)
  dst.append(out)
  dst.append(duration)
  
def index_in_track(clipitem):
    ### This clip is the nth clip in that track that contains it.
    track = clipitem.getparent()
    clipid = clipitem.get("id")
    index = 0
    for item in track.getchildren():
      if item.tag != clipitem.tag:  #  outputchannelindex goes in a track, just like a clipitem, can throw off indexes.  Why not just use names?!
        continue
      index += 1
      itemid = item.get("id")
      if itemid == clipid:
        return index
    return -1
    
def index_in_parent(child):
    ### This child node is the nth child if its parent.  Probably not what you want for a clipitem in a track.
    parent = child.getparent()
    index = 0
    for item in parent.getchildren():
      index += 1
      if item == child:
        return index
    return -1
  
def link_clips(clips):
    ### Link clips, so when you click and drag one, the other move along with it.  Can link a clip's audio to the clip's video.
    
    # XMEML is fussy with all items in a group being in 100% agreement about being linked with each other.
    # At least in Premiere, linking a video clip to the audio, without also doing the reverse, accomplishes nothing.
    # I no longer have a copy of FCP7 to compare to the original behavior.
    
    # Oh, and you have reference clipitems with identical id's but you can't properly link (by id) to both of them...
    
    if verbose: print("Linking", clips)
    for clip in clips:
      clip_id = clip.get("id")
      if verbose: print("  Working on", clip_id, index_in_track(clip))
      for inner_clip in clips:
      
          inner_id = inner_clip.get("id")
          
          link = etree.SubElement(clip, "link")
          
          linkclipref = etree.SubElement(link, "linkclipref")
          linkclipref.text = inner_id
          
          trackindex = etree.SubElement(link, "trackindex")
          trackindex.text = str(index_in_parent(inner_clip.getparent())) 
          
          clipindex = etree.SubElement(link, "clipindex")
          clipindex.text = str(index_in_track(inner_clip))
          
          mediatype = etree.SubElement(link, "mediatype")   # <mediatype>video</mediatype>
          if "audio" in inner_id:
            mediatype.text = "audio"
          else:
            mediatype.text = "video"
          if verbose: print("      to", inner_id, index_in_track(inner_clip), inner_clip.getparent().getchildren())
          
        

def add_atrack(a, channel):
    # incomplete (?) Track details can make Premiere go wacky.
    trackdetails = {"MZ.TrackTargeted": "1", "premiereTrackType": "Stereo"}
    atrack = etree.SubElement(a, "track")
    ch_idx = etree.SubElement(atrack, "outputchannelindex")
    ch_idx.text = str(channel)
    return atrack
    
def add_audioclipitem(parent_track, reference_video_clipitem, namesuffix = ""):
    clipname = reference_video_clipitem.find("name").text.split(".")[0]
    file = reference_video_clipitem.find("file")
    audioclipid = "audio" + reference_video_clipitem.get("id") + namesuffix
    audioclipitem = etree.SubElement(parent_track, "clipitem", id=audioclipid)
    
    amaster = etree.SubElement(audioclipitem, "masterclipid")
    amaster.text = clipname
    
    aname = etree.SubElement(audioclipitem, "name")
    aname.text = clipname

    afile = etree.SubElement(audioclipitem, "file", id=file.get('id'))
    copy_timing(reference_video_clipitem, audioclipitem)

    return audioclipitem

    
    
clipitem_cache = {}
last_relink_id = 1

def dereference_video_clipitem(clipitem, reference_clipitem):
    last_relink_id = 1
    parent = clipitem.getparent()
    item_id = clipitem.get("id")
    new_id = "relinked-"+item_id+"-"+str(last_relink_id)
    last_relink_id += 1
    new_clipitem = copy.copy(reference_clipitem)
    new_clipitem.set("id", new_id)
    parent.replace(clipitem, new_clipitem)
    return new_clipitem
    
    
    
def add_xml_audio_track(a, v):
    ### Takes XML [xmeml/project/children/sequence/media/audio] and [.../video] objects
    global clipitem_cache
    
    clips = v.find('./track').getchildren()
    # Two audio tracks for stereo, channels 1 and 2.
    atrack_a = add_atrack(a, 1)
    atrack_b = add_atrack(a, 2)
    
    for clipitem in clips:
      if verbose: print("    Clipitem ", clipitem)
      item_id = clipitem.get("id")
      if clipitem.getchildren() == []:
        # For brevity, one item can be a reference to another item.
        # The result is than an entire track just looks like:
        # <track><clipitem id="clipitem-1"/></track>
        if verbose: print("      Has no children.  Dereferencing.")
        reference_clipitem = clipitem_cache[item_id]
        clipitem = dereference_video_clipitem(clipitem, reference_clipitem)
      else:
        clipitem_cache[item_id] = clipitem

      # print(clipitem.getchildren())
      a_item = add_audioclipitem(atrack_a, clipitem, namesuffix = "")
      b_item = add_audioclipitem(atrack_b, clipitem, namesuffix = "-b")
      url = clipitem.find('file/pathurl')

      link_clips([clipitem, a_item, b_item])

      
    return    
                        
                        
