"""Package only a successfully tested GBA build, with traceable checksums."""
from pathlib import Path
import argparse,hashlib,json,os,shutil

def main():
 ap=argparse.ArgumentParser();ap.add_argument('build',type=Path);a=ap.parse_args();root=a.build
 rom=root/'sia2_lab.gba';data=rom.read_bytes()
 if not 192<=len(data)<=32*1024*1024:raise SystemExit('Invalid GBA ROM size')
 if (sum(data[160:190])+0x19)&255:raise SystemExit('Invalid GBA header checksum')
 if data[178]!=0x96 or b'SRAM_V113' not in data:raise SystemExit('Missing GBA header or SRAM identifier')
 passed=[]
 with (root/'emulator-report.txt').open() as report:
  for line in report:
   if line.startswith('PASS '):passed.append(line.rstrip())
 if not any(s.startswith('PASS frontend ') for s in passed) or not any(s.startswith('PASS settings integration:') for s in passed):
  raise SystemExit('Both gameplay and settings emulator PASS reports are required')
 pictures=[p.with_suffix('.png') for p in sorted(root.glob('*.ppm'))]
 if any(not p.exists() for p in pictures):raise SystemExit('Export every emulator PPM before packaging')
 if not pictures:raise SystemExit('Missing actual emulator captures')
 out=root/'release'
 if out.exists():shutil.rmtree(out)
 out.mkdir();shutil.copyfile(rom,out/'Lady_Sia2_GBA_test.gba')
 (out/'TEST_REPORT.txt').write_text('\n'.join(passed)+'\n')
 shutil.copyfile(root/'position-audit.json',out/'position-audit.json')
 (out/'screenshots').mkdir()
 for path in pictures:shutil.copyfile(path,out/'screenshots'/path.name)
 info={'source_commit':os.environ.get('GITHUB_SHA','not-specified'),'rom_sha256':hashlib.sha256(data).hexdigest(),'rom_bytes':len(data),'screenshots':len(pictures),'hardware_tested':False,'disk_save_reload_tested':False,'music':'Existing mixed recording; separation trials are not integrated.'}
 (out/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n')
 (out/'LEGGIMI.txt').write_text('''LADY SIA 2 - BUILD DI TEST\n\nApri Lady_Sia2_GBA_test.gba in un emulatore GBA.\nÈ una ricostruzione parziale: cinque inquadrature parziali del livello 1, due guardie prototipo e quattro gemme.\nIl percorso completo e gli altri livelli non sono ancora giocabili.\n\nA: conferma/salto. B: indietro/attacco.\nFrecce: movimento. Salta sotto il bordo per aggrapparti; Su/A: risali; Giu: lascia la presa. Start: pausa.\nSelect: menu. R: ripristino delle aree e delle gemme.\nTre vite e tre HP (provvisori). Colpi nemici consumano HP; colpi letali e cadute consumano una vita.\nRespawn: HP pieni, gemme e nemici sconfitti conservati. Zero vite: Game Over.\nHP e vite consultabili nella pausa; nessun riquadro HP/L sovrapposto allo scenario.\nPLAY apre direttamente i dialoghi iniziali: il filmato INTRO e la relativa opzione sono stati rimossi.\n\nSOUND viene salvato in SRAM; il vecchio flag INTRO non abilita più il filmato. Il reset del core è verificato;\nriapertura del file .sav e hardware reale non ancora verificati.\nLa musica usa ancora la registrazione precedente.\nNon è stato integrato il tentativo di separazione degli effetti.\n\nTEST_REPORT.txt: prove mGBA superate.\nBUILD_INFO.json: commit, hash ROM e limiti.\nSHA256SUMS.txt: integrità di tutti gli altri file del pacchetto.\nscreenshots/: acquisizioni reali della ROM compilata.\n''')
 repo=Path(__file__).resolve().parents[1]
 for source in ['previews/ledge_gameplay.gif','references/LEDGE_STATUS.md','docs/progress.svg']:
  shutil.copyfile(repo/source,out/Path(source).name)
 files=sorted(p for p in out.rglob('*') if p.is_file())
 (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(out).as_posix()+'\n' for p in files))
 print('Packaged',len(data),'ROM bytes and',len(pictures),'real captures in',out)
if __name__=='__main__':main()
