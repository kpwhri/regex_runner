import datetime
import pathlib
from loguru import logger


try:
    import pandas as pd
except ImportError:
    logger.warning('Need to install pandas: `pip install pandas`.')
    raise

from runrex.text import Document


def build_review_lists(output_file: pathlib.Path, log_file: pathlib.Path, metafile: pathlib.Path):
    outdir = output_file.parent
    logger.info(f'Output files for review will be placed in {outdir}.')
    if output_file.name.endswith('jsonl'):
        rr_df = pd.read_json(output_file, lines=True)
        # with raw jsonl, update certain variable names
        rr_df['doc_id'] = rr_df['name'].astype(int)
        rr_df['start_idx'] = rr_df['start']
        rr_df['end_idx'] = rr_df['end']
    elif output_file.name.endswith('csv'):
        rr_df = pd.read_csv(output_file)
        rr_df['doc_id'] = rr_df['doc_id'].astype(int)
    else:
        raise ValueError(f'Unable to interpret filetype of {output_file}; expected "jsonl" or "csv".')

    meta_df = pd.read_csv(metafile)
    meta_df['doc_id'] = meta_df['doc_id'].astype(int)
    mdf = pd.merge(meta_df, rr_df, how='inner', on='doc_id')
    mdf['algocat'] = mdf.apply(lambda r: f'{r["algorithm"]}_{r["category"]}', axis=1)

    log_df = pd.read_json(log_file, lines=True)
    log_df = log_df.rename(columns={'text': 'term'})
    log_df['algocat'] = log_df.apply(lambda r: f'{r["algorithm"]}_{r["category"]}', axis=1)
    log_df['match'] = log_df['matches'].apply(lambda x: x[0])
    log_df['matches'] = log_df['matches'].apply(lambda x: ', '.join(set(x)))
    df = pd.merge(mdf, log_df, how='left',
                  left_on=['doc_id', 'algocat', 'start', 'end'],
                  right_on=['name', 'algocat', 'start', 'end'])[
        ['doc_id', 'algocat', 'text', 'term', 'start_idx', 'end_idx', 'match', 'matches']
    ].drop_duplicates()

    # process file
    algocats = set(df['algocat'].unique())

    offset = 150
    for algocat in sorted(algocats):
        curr_df = df[df.algocat == algocat].sample(frac=1)
        res = []
        for i, r in enumerate(curr_df.itertuples()):
            start = r.start_idx
            end = r.end_idx
            text = Document.clean_text(r.text)
            term = r.term.strip()
            context = text[max(0, start - offset): end + offset].strip()
            start_idx = context.index(term)
            end_idx = start_idx + len(term)
            precontext = text[max(0, start_idx - offset): start_idx].strip()
            postcontext = text[end_idx + 1: end_idx + offset].strip()
            res.append({
                'index': i,
                'doc_id': r.doc_id,
                'algocat': r.algocat,
                'precontext': precontext,
                'term': r.term,
                'postcontext': postcontext,
            })
        out_df = pd.DataFrame(res)
        out_df.to_csv(
            outdir / f'{algocat}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            index=False
        )
        logger.info(f'Output for {algocat} contains {out_df.shape[0]} records.')
