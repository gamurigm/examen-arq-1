"""Valida entradas documentales sin modificar entregables ni leer secretos."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import zipfile


def validate(profile_path, final=False):
    root = profile_path.resolve().parent
    profile = json.loads(profile_path.read_text(encoding='utf-8-sig'))
    errors, records = [], []
    artifacts = profile['documentation']['artifacts']
    if len(artifacts) != 4:
        errors.append('Se requieren cuatro entregables.')
    for key, artifact in artifacts.items():
        record = {'artifact': key}
        for field in ('source', 'template'):
            path = root / artifact[field]
            if not path.is_file():
                errors.append(f'{key}: falta {field}: {path}')
                continue
            record[field + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            if field == 'template':
                try:
                    with zipfile.ZipFile(path) as package:
                        if package.testzip():
                            errors.append(f'{key}: plantilla corrupta')
                except zipfile.BadZipFile:
                    errors.append(f'{key}: plantilla Office invalida')
            else:
                content = path.read_text(encoding='utf-8-sig')
                if final and re.search(r'REVISION PENDIENTE|SCREENSHOT PENDING|\bTODO\b|<project-id>', content, re.I):
                    errors.append(f'{key}: contiene marcadores pendientes')
                for image in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', content):
                    if not (path.parent / image).is_file():
                        errors.append(f'{key}: imagen ausente: {image}')
        records.append(record)
    if final:
        review = root / profile['documentation'].get('visual_review', '05. DOCUMENTACION/revision-visual.json')
        if not review.is_file():
            errors.append('Falta registro de revision visual de todas las paginas y diapositivas.')
        errors.append('Promocion final deshabilitada hasta implementar y verificar renderizado y trazabilidad.')
    return {'source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
            'final': final, 'artifacts': records, 'errors': errors, 'passed': not errors}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=pathlib.Path, default=pathlib.Path('documentation-profile.json'))
    parser.add_argument('--final', action='store_true')
    args = parser.parse_args()
    result = validate(args.profile, args.final)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['passed'] else 1)
