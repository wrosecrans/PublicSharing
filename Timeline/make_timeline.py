
import os
import docopt

import opentimelineio
otio = opentimelineio

import ffmpeg
from lxml import etree
import xmeml



helptext = """
  Usage: make_timeline.py [options] [<FILE>...]

  --ffprobe=path          Generate a shotdb.metadata.json with with and codec metadata.
  --seq name     Import a QuantumCut JSON script.
  --out filename     Final Result XML File name with everything linked
  --intermediate filename  Initial Result XML File name
  --verbose         Shout.
  --quiet           Don't shout.

"""

verbose = True
ffprobep = 'ffprobe'  # Set to a full path if you want to run a specific binary.
# ffprobep = "C:\\Users\\wrose\\Documents\\development\\vcpkg\\installed\\x64-windows\\bin\\ffprobe.exe"
intermediate_filename = "result.xml"
output_filename = "result.linked.xml"
sequence_name = "Sequence"

args = docopt.docopt(helptext)
# print(args)

if args['--verbose']:
    verbose = True
if args['--quiet']:
    verbose = False
    
if args['--ffprobe']:
    ffprobep = args['--ffprobe']
if args['--out']:
    output_filename = args['--out']
if args['--intermediate']:
    intermediate_filename = args['--intermediate']
if args['--seq']:
    sequence_name = args['--seq']


metadata = {}
def duration(video_file):
    global metadata
    if not video_file in metadata:
        # if verbose: print("Probing ", video_file)
        metadata[video_file] = ffmpeg.probe(video_file, ffprobep)
        # if verbose: print("  Duration", float(metadata[video_file]["format"]["duration"]))
    return float(metadata[video_file]["format"]["duration"])
        

def timerange(video_file, framerate=23.976):
    frames = duration(video_file) * framerate
    
    range = otio.opentime.TimeRange(
        start_time=otio.opentime.RationalTime(value=0, rate=framerate),
        duration = otio.opentime.RationalTime(value=frames, rate=framerate)
        )
    return range

def make_sequence(name, shots, framerate=23.976):
    print("Making ", name)
    stack = opentimelineio.schema.Stack()
    tl = opentimelineio.schema.Timeline(name=name, tracks=stack)
    tl.tracks.name = name
    track = otio.schema.Track(kind="Video")
    tl.tracks.append(track)
    for shot in shots:
        print("  With ", shot)
        src_range = timerange(shot)
        mref = media_reference=otio.schema.ExternalReference(target_url=shot)
        mref.available_range=src_range
        clip = otio.schema.Clip(name=os.path.basename(shot), media_reference=mref, source_range=src_range)
        track.append(clip)
    return tl

def write_xml(sequences, result_xml_filename):
    otio_timelines = opentimelineio.schema.SerializableCollection()

    for s in sequences:
        tl = make_sequence(s["name"], s["clips"])
        otio_timelines.append(tl)

    opentimelineio.adapters.write_to_file(otio_timelines, result_xml_filename)



def fix_xml(input_file, output_file):
    with open(input_file, 'r') as f:
        tree = etree.parse(f)
    children = tree.findall('./project/children/')
    top_bin = xmeml.make_bin("Timelines", parent=tree.find('./project/children'), label="random")
    # if verbose: print(children)
    for seq in children:
        name = seq.find('./name').text
        if verbose: print("  Linking ", name)

        v = seq.find('./media/video')
        a = seq.find('./media/audio')

        v.append(xmeml.xml_video_format("sequence"))
        xmeml.set_seq_audio_fmt(a)
        xmeml.add_xml_audio_track(a,v)
        
        tl_bin = xmeml.make_bin(name, label="random")
        xmeml.put_in_bin(tl_bin, seq)
        xmeml.put_in_bin(top_bin, tl_bin)
        
    etree.indent(tree)
    with open(output_file, 'wb') as f:
        tree.write(f, pretty_print=True)


if args['<FILE>']:
    clips = []
    for clip in args['<FILE>']:
        clips.append(os.path.abspath(clip))

sequence = {"name": sequence_name, "clips": clips}

# Write an XML file, but it will only have video.
write_xml([sequence], intermediate_filename)

# Tidy up that XML so the video clips have linked audio.
fix_xml(intermediate_filename, output_filename)



