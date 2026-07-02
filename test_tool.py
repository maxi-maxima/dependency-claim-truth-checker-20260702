from dependency_claim_truth_checker import check

def test_zero_dependency_claim_fails(tmp_path):
    (tmp_path/'README.md').write_text('Zero dependencies and works offline')
    (tmp_path/'requirements.txt').write_text('requests==2.0')
    r=check(tmp_path, tmp_path/'README.md')
    assert not r['passed']
    assert r['findings'][0]['claim']=='zero_dependencies'
