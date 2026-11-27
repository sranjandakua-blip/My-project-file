# Contact sheet of the final video at given times: python3 contact_sheet.py out.mp4 sheet.png 0.5 3 9 ...
import sys,subprocess,os
vid,png,ts=sys.argv[1],sys.argv[2],sys.argv[3:]
args=[];[args.extend(['-ss',t,'-i',vid]) for t in ts]
n=len(ts); fc=''.join(f'[{i}:v]scale=240:-1[v{i}];' for i in range(n))+''.join(f'[v{i}]' for i in range(n))+f'hstack=inputs={n}[o]'
subprocess.run(['ffmpeg','-v','error','-y',*args,'-filter_complex',fc,'-map','[o]','-frames:v','1',png],check=True)
