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
 for prefix in ['PASS airborne integration:', 'PASS ledge integration:', 'PASS scenery integration:', 'PASS disk save integration:', 'PASS reset input integration:', 'PASS menu cancel integration:', 'PASS continuation integration:', 'PASS bridge run integration:', 'PASS upper route integration:', 'PASS upper revisit integration:']:
  if not any(s.startswith(prefix) for s in passed):raise SystemExit('Missing '+prefix)
 pictures=[p.with_suffix('.png') for p in sorted(root.glob('*.ppm'))]
 if not any(s.startswith('PASS pickup death integration:') for s in passed):
  raise SystemExit('Missing PASS pickup death integration:')
 if not any(s.startswith('PASS island gap integration:') for s in passed):
  raise SystemExit('Missing PASS island gap integration:')
 if not any(s.startswith('PASS ramp route integration:') for s in passed):
  raise SystemExit('Missing PASS ramp route integration:')
 if any(not p.exists() for p in pictures):raise SystemExit('Export every emulator PPM before packaging')
 if not pictures:raise SystemExit('Missing actual emulator captures')
 out=root/'release'
 if out.exists():shutil.rmtree(out)
 out.mkdir();shutil.copyfile(rom,out/'Lady_Sia2_GBA_test.gba')
 (out/'TEST_REPORT.txt').write_text('\n'.join(passed)+'\n')
 shutil.copyfile(root/'position-audit.json',out/'position-audit.json')
 (out/'screenshots').mkdir()
 for path in pictures:shutil.copyfile(path,out/'screenshots'/path.name)
 info={'source_commit':os.environ.get('GITHUB_SHA','not-specified'),'rom_sha256':hashlib.sha256(data).hexdigest(),'rom_bytes':len(data),'screenshots':len(pictures),'overall_completion_estimate_percent':sum(r['earned'] for r in json.loads((Path(__file__).resolve().parents[1]/'docs/progress.json').read_text())['areas']),'playable_viewports':12,'collision_geometry':'provisional','hardware_tested':False,'disk_save_reload_tested':True,'music':'Existing mixed recording; separation trials are not integrated.'}
 (out/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n')
 (out/'LEGGIMI.txt').write_text('''LADY SIA 2 - BUILD DI TEST\n\nApri Lady_Sia2_GBA_test.gba in un emulatore GBA.\nÈ una ricostruzione parziale: dodici inquadrature parziali del livello 1, tre guardie prototipo e cinque gemme.\nLe nuove aree aggiungono salita, vuoto, ponte, terza guardia, parete, piattaforma superiore due viste della rampa e il salto fra le isole successive con collisioni provvisorie.\nIl percorso completo e gli altri livelli non sono ancora giocabili.\n\nSu+A+sinistra dalla parete: salto alto provvisorio verso la piattaforma superiore.\nSulla piattaforma superiore prosegui a sinistra: risali la rampa fino alla nuova isola. Prosegui a sinistra e salta il vuoto verso l'isola successiva; Su+A raggiunge il ripiano alto provvisorio.
A: conferma/salto. B: indietro/attacco.\nFrecce: movimento. Salta sotto il bordo per aggrapparti; Su/A: risali; Giu: lascia la presa. Start: pausa.\nSelect: menu. R: ripristino delle aree e delle gemme.\nTre vite e tre HP (provvisori). Colpi nemici consumano HP; colpi letali e cadute consumano una vita.\nRespawn: HP pieni, gemme e nemici sconfitti conservati. Zero vite: Game Over.\nHP e vite consultabili nella pausa; nessun riquadro HP/L sovrapposto allo scenario.\nPLAY apre direttamente i dialoghi iniziali: il filmato INTRO e la relativa opzione sono stati rimossi.\n\nSOUND viene salvato in SRAM; il vecchio flag INTRO non abilita più il filmato. Il reset del core è verificato;\nriapertura del file SRAM verificata con nuove istanze mGBA, SOUND spento/acceso e checksum corrotto.\nHardware reale non ancora verificato.\nLa musica usa ancora la registrazione precedente.\nNon è stato integrato il tentativo di separazione degli effetti.\n\nTEST_REPORT.txt: prove mGBA superate.\nBUILD_INFO.json: commit, hash ROM e limiti.\nSHA256SUMS.txt: integrità di tutti gli altri file del pacchetto.\nscreenshots/: acquisizioni reali della ROM compilata.\n''')
 repo=Path(__file__).resolve().parents[1]
 shutil.copyfile(repo/'references/LIFE_FEEDBACK_STATUS.md',out/'LIFE_FEEDBACK_STATUS.md')
 shutil.copyfile(repo/'references/RAMP_ROUTE_STATUS.md',out/'RAMP_ROUTE_STATUS.md')
 for source in ['previews/ramp_gameplay.gif','previews/ramp_preview.json','previews/ramp_upper_landing.png','previews/ramp_lower_entry.png','assets/ramp_route_manifest.json']:
  shutil.copyfile(repo/source,out/Path(source).name)
 for source in ['references/ISLAND_GAP_STATUS.md','previews/island_gap_gameplay.gif','previews/island_gap_preview.json','previews/island_gap_left_landing.png','previews/island_gap_high_ledge.png','assets/island_gap_manifest.json']:
  shutil.copyfile(repo/source,out/Path(source).name)
 for name in ['jump','ledge','scenery','continuation','bridge_run','ramp','island_gap']:
  report=json.loads((repo/'previews'/f'{name}_preview.json').read_text())
  preview=(repo/'previews'/f'{name}_gameplay.gif').read_bytes()
  if len(preview)!=report.get('gif_bytes') or hashlib.sha256(preview).hexdigest()!=report.get('gif_sha256'):
   raise SystemExit('Corrupt or stale animation bytes: '+name)
  if report['rom_sha256']!=hashlib.sha256(data).hexdigest() or not report['all_source_pixels_preserved']:
   raise SystemExit('Stale or unverified native animation preview: '+name)
 for source in ['references/UPPER_ROUTE_PLAYABLE_STATUS.md','previews/upper_entry.png','previews/upper_gem5.png','previews/upper_return.png','previews/bridge_run_gameplay.gif','previews/bridge_run_preview.json','references/BRIDGE_RUN_PLAYABLE_STATUS.md','previews/continuation_gameplay.gif','previews/continuation_preview.json','references/CONTINUATION_PLAYABLE_STATUS.md','previews/scenery_gameplay.gif','previews/scenery_preview.json','references/SCENERY_STATUS.md','previews/jump_gameplay.gif','previews/jump_preview.json','previews/ledge_gameplay.gif','previews/ledge_preview.json','references/JUMP_STATUS.md','references/LEDGE_STATUS.md','references/SAVE_RELOAD_STATUS.md','references/RESET_INPUT_STATUS.md','references/MENU_CANCEL_STATUS.md','docs/progress.svg','docs/progress.png','docs/progress.json','docs/PROGRESS.md']:
  shutil.copyfile(repo/source,out/Path(source).name)
 files=sorted(p for p in out.rglob('*') if p.is_file())
 (out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(out).as_posix()+'\n' for p in files))
 print('Packaged',len(data),'ROM bytes and',len(pictures),'real captures in',out)
if __name__=='__main__':main()
