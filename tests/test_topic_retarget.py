import copy
from datetime import date
import json
from pathlib import Path
import sqlite3
import unittest

from radar import dashboard, store
from radar.score import Matcher, eligible
from radar.util import now

CFG=json.loads((Path(__file__).resolve().parents[1]/'config/config.json').read_text())
TODAY=now().date()


def scored(title,abstract='',**updates):
    item={'title':title,'abstract':abstract,'source':'arxiv','kind':'paper',
          'venue':'arXiv','authors':'','published':TODAY,'extra':{}}
    item.update(updates)
    return Matcher(CFG).score(item,TODAY)


class TopicRetargetTests(unittest.TestCase):
    def test_diffusion_for_molecules_is_chemical_generation(self):
        item=scored('Equivariant diffusion models for molecular generation')
        self.assertIn('gen-model',item['topics']);self.assertTrue(eligible(CFG,item))

    def test_flow_for_reactions_is_chemical_generation(self):
        item=scored('Flow matching for reaction pathway generation')
        self.assertIn('gen-model',item['topics']);self.assertTrue(eligible(CFG,item))

    def test_crystal_generation_gets_crystal_topic(self):
        item=scored('A generative diffusion model for crystal structure generation')
        self.assertIn('crystal-gen',item['topics']);self.assertTrue(eligible(CFG,item))

    def test_general_video_is_lower_priority_and_not_chemical_generation(self):
        item=scored('Video generation with diffusion models and text-to-video synthesis')
        self.assertNotIn('gen-model',item['topics']);self.assertIn('vision-gen',item['topics'])
        self.assertFalse(eligible(CFG,item))

    def test_video_news_cannot_bypass_adjacent_threshold(self):
        item=scored('Video generation with diffusion models',kind='news')
        self.assertFalse(eligible(CFG,item))

    def test_physical_diffusion_is_not_generative_model(self):
        item=scored('Foundation model for hydrogen diffusion in molecular crystals')
        self.assertNotIn('gen-model',item['topics'])
        self.assertNotIn('crystal-gen',item['topics'])

    def test_nonchemical_flow_math_stays_in_math_topic(self):
        item=scored('Optimal transport and Wasserstein analysis of flow matching')
        self.assertNotIn('gen-model',item['topics']);self.assertIn('gen-math',item['topics'])

    def test_organic_ferroelectric_first_principles(self):
        item=scored('Database mining and first-principles assessment of organic proton-transfer ferroelectrics')
        self.assertIn('ferro-calc',item['topics']);self.assertTrue(eligible(CFG,item))

    def test_polarization_simulation_in_named_molecular_material(self):
        item=scored('Ferroelectric polarization switching in croconic acid',
                    'Ab-initio molecular dynamics predicts proton transfer and the switching barrier.')
        self.assertIn('ferro-calc',item['topics'])

    def test_organic_inorganic_hybrid_ferroelectric_computation(self):
        item=scored('First principles calculations of ferroelectricity in hybrid organic-inorganic perovskites')
        self.assertIn('ferro-calc',item['topics'])

    def test_polymer_ferroelectric_computation(self):
        item=scored('DFT calculation of ferroelectric polarization switching in PVDF')
        self.assertIn('ferro-calc',item['topics'])

    def test_machine_learned_relaxation_is_also_ferroelectric_computation(self):
        item=scored('Synthesis-by-design of ferroelectric hybrid organic-inorganic perovskites',
                    'Machine-learned interatomic-potential relaxation ranks organic spacers.')
        self.assertIn('ferro-calc',item['topics'])

    def test_experiment_only_ferroelectric_has_no_computation_tag(self):
        item=scored('Synthesis and measurement of organic ferroelectric crystals')
        self.assertNotIn('ferro-calc',item['topics'])

    def test_plain_oxide_calculation_not_organic_ferroelectric_topic(self):
        item=scored('First principles calculation of ferroelectricity in barium titanate')
        self.assertNotIn('ferro-calc',item['topics'])

    def test_chiral_crystal_packing(self):
        item=scored('Crystal packing of enantiopure and racemic organic molecules')
        self.assertIn('chiral-crystal',item['topics']);self.assertTrue(eligible(CFG,item))

    def test_chiral_resolution_spellings(self):
        for spelling in ['crystallization','crystallisation']:
            with self.subTest(spelling=spelling):
                item=scored('Preferential '+spelling+' and chiral resolution of organic molecules')
                self.assertIn('chiral-crystal',item['topics'])

    def test_chirality_from_achiral_molecular_building_blocks(self):
        item=scored('Spontaneous chiral symmetry breaking in a molecular crystal',
                    'Achiral organic molecules form a homochiral crystal packing.')
        self.assertIn('chiral-crystal',item['topics'])

    def test_chiral_photonic_and_weyl_crystals_have_no_molecular_tag(self):
        for title in ['Chiral photonic crystals for light control','Chiral Weyl fermions in silicon crystals']:
            self.assertNotIn('chiral-crystal',scored(title)['topics'])

    def test_solution_asymmetric_catalysis_without_solid_context(self):
        item=scored('Enantioselective synthesis of chiral organic molecules in solution')
        self.assertNotIn('chiral-crystal',item['topics'])

    def test_invalid_and_group_is_rejected(self):
        cfg=copy.deepcopy(CFG);cfg['topics'][0]['require_all_groups']=[[]]
        with self.assertRaises(ValueError):Matcher(cfg)

    def test_weight_and_retrieval_priorities(self):
        topics={t['id']:t for t in CFG['topics']}
        self.assertEqual(topics['vision-gen']['weight'],0.35)
        self.assertEqual(topics['vision-gen']['tier'],'adjacent')
        self.assertEqual(len(CFG['topics']),9)
        queries=CFG['sources']['openalex']['queries']
        self.assertIn('molecular generation diffusion model',queries)
        self.assertIn('organic ferroelectric first principles',queries)
        self.assertIn('chiral molecular crystal',queries)
        self.assertNotIn('video generation diffusion transformer',queries)

    def test_dashboard_reweights_in_memory_preserving_stored_data(self):
        conn=sqlite3.connect(':memory:');conn.row_factory=sqlite3.Row
        self.addCleanup(conn.close);conn.executescript(store.SCHEMA)
        for key,title,score in [('old-video','Video generation with diffusion models',99),
                               ('old-ferro','First principles study of organic ferroelectric proton transfer',0)]:
            conn.execute('''INSERT INTO items(key,kind,source,sources,title,abstract,authors,venue,
                published,first_seen,score,topics,matched,extra) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (key,'paper','arxiv','arxiv',title,'Abstract.','','arXiv',TODAY.isoformat(),
                 TODAY.isoformat()+'T12:00:00',score,'["gen-model"]','[]','{}'))
        conn.commit()
        before=[tuple(row) for row in conn.execute('SELECT * FROM items ORDER BY key')]
        data=dashboard.collect(CFG,conn)
        self.assertEqual([item['k'] for item in data['items']],['old-ferro'])
        self.assertIn('ferro-calc',data['items'][0]['tp'])
        self.assertEqual(before,[tuple(row) for row in conn.execute('SELECT * FROM items ORDER BY key')])


if __name__=='__main__':unittest.main()
