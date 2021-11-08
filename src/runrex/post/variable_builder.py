"""
Build variables defined in a Python dictionary from the algorithms/categories.

1. Run runrex for your application
2. Use `extract_and_load_json.py` script to format the results into a csv file
3. Run this file on that output along with a table defined as follows:

| doc_id | patient_id | total_text_length | date | other variables, e.g., 'is_radiology' |
------------------------------------------------------------------------------------------

"""
import pathlib

import pandas as pd
import numpy as np
from functools import reduce
from loguru import logger


def density(name, df, value, is_algo=True, by_date=False, by_extra=False,
            cutoff=1, normalize=None):
    kind = 'algorithm' if is_algo else 'category'
    gb_lst = ['patient_id']
    if by_date:
        gb_lst.append('date')
    if by_extra:
        res = df[(df[kind] == value) & (df[by_extra])].groupby(gb_lst)[kind].nunique()
    else:
        res = df[df[kind] == value].groupby(gb_lst)[kind].nunique()
    res = res.reset_index()
    res = res[res[kind] >= cutoff]
    if res.shape[0] == 0:
        return pd.Series(name=name,
                         index=df['patient_id'].unique(),
                         dtype='float')
    if normalize:
        if by_date:
            if isinstance(next(normalize.keys()), tuple):
                res[name] = res.groupby(['patient_id', 'date'])[kind].sum().reset_index().apply(
                    lambda x: x[kind] / normalize[(x['patient_id'], x['date'])],
                    axis=1
                )
            else:
                res[name] = res.groupby(['patient_id', 'date'])[kind].sum().reset_index().apply(
                    lambda x: x[kind] / normalize[x['patient_id']],
                    axis=1
                )
            res = res.groupby('patient_id')[name].sum()
        else:
            res[name] = res.groupby('patient_id')[kind].sum().reset_index().apply(
                lambda x: x[kind] / normalize[x['patient_id']],
                axis=1
            )
            del res[kind]
            res = res.groupby('patient_id')[name].sum().rename(name)
    return res
    # if res.shape[0] > 0:
    #     return res.rename(name)
    # else:
    #     return pd.Series(name=name, dtype='int64')


def filter_condition(name, stacked_df, algorithms, categories, normalize, *conditions, extra_condition=None):
    """

    :param name:
    :param stacked_df:
    :param algorithms:
    :param categories:
    :param normalize:
    :param conditions: name -> tuple of features()
        * e.g., 'acute_panc_consistent': ('+pancreatitis_ACUTE', '+is_radiology'),
        `+`: [category or algorithm]include these (AND-ed together; requires all to be positive)
        `-`: [category or algorithm] exclude these (OR-ed together; requires all to be negative)
        `!`: [category] used with `+`; include everything in `+` (an algorithm) except the category following `!`
                (exclude just one category from the algorithm)
        `=`: [category] exclude everything in the relevant algorithm except this category
                (include just one category from the algorithm); doesn't use with `-` for the algorithm
    :return:
    """
    filters = []
    for condition in conditions:
        label = condition[1:]
        if label not in algorithms and label not in categories and label != extra_condition:
            logger.info(f'Missing {condition[1:]} for condition {name}. This is not required, so continuing to create.')
            if condition[0] in {'+'}:  # this required
                logger.warning(
                    f'Failed to create condition: {name} ({conditions}) due to {condition} not being present.')
                return pd.Series(name=name, dtype='int64')
            elif condition[0] not in {'='}:
                continue
        if condition.startswith('+'):
            filters.append(stacked_df[label] >= 1.0)
        elif condition.startswith('-'):
            filters.append(stacked_df[label] == 0.0)
        elif condition.startswith('!'):  # allow all in algorithm except this one (disallow just this one)
            for algo in algorithms:
                if label.startswith(algo):
                    filters.append(stacked_df[label] < stacked_df[algo])
                    break
        elif condition.startswith('='):  # disallow all in algorithm except this one (allow just this one)
            if label not in categories:  # don't need to allow this special case
                for algo in algorithms:
                    if label.startswith(algo):
                        logger.info(
                            f'Exception condition does not exist for {name} ({condition}), just setting {algo} to 0.0.')
                        filters.append(stacked_df[algo] == 0.0)
                        break
                continue
            for algo in algorithms:
                if label.startswith(algo):
                    filters.append(stacked_df[label] == stacked_df[algo])  # all must be the exception case
                    break
    if not conditions:
        logger.warning(f'No condition created for {name} ({conditions}). Skipping')
    res = stacked_df[
        reduce(np.logical_and, filters)
    ].reset_index().groupby('patient_id')['date'].nunique().reset_index()
    if res.shape[0] > 0:
        res[name] = res.apply(lambda x: x['date'] / normalize[x['patient_id']], axis=1)
        del res['date']
        res = res.groupby('patient_id')[name].sum().rename(name)
    else:
        res = pd.Series(name=name,
                        index=stacked_df.reset_index()['patient_id'].unique(),
                        dtype='float')
    return res
    # if res.shape[0] > 0:
    #     return res.rename(name)
    # else:
    #     return pd.Series(name=name, dtype='int64')


def prepare_datasets(data_path, meta_path, extra_condition=None):
    data = pd.read_csv(data_path)
    meta = pd.read_csv(meta_path)
    # build look ups for normalization
    patid_to_text_length = meta.groupby('patient_id')['total_text_length'].sum().to_dict()
    patid_date_to_note_count = meta.groupby(['patient_id', 'date'])['doc_id'].count().to_dict()
    # merge tables together
    data['doc_id'] = data['doc_id'].astype(int)
    meta['doc_id'] = meta['doc_id'].astype(int)
    df = pd.merge(data, meta, how='inner', on='doc_id')
    # build dataframes
    if 'patient_id' in meta.columns:
        del meta['patient_id']
    df = df[['patient_id', 'algorithm', 'category'] + list(meta.columns)]
    del df['doc_id']
    del df['total_text_length']
    df['category'] = df.apply(lambda x: f"{x['algorithm']}_{x['category']}", axis=1)
    stacked_df = pd.merge(
        df.pivot_table(index=['patient_id', 'date'], columns='algorithm', aggfunc='count')['category'],
        df.pivot_table(index=['patient_id', 'date'], columns='category', aggfunc='count')['algorithm'],
        left_index=True,
        right_index=True,
        how='inner'
    ).fillna(0.0)
    if extra_condition:
        stacked_df = pd.merge(
            df.groupby(['patient_id', 'date'])[extra_condition].max(),
            stacked_df,
            left_index=True,
            right_index=True,
            how='inner'
        ).fillna(0.0)
    # get other items
    algorithms = df['algorithm'].unique()
    categories = df['category'].unique()
    return df, stacked_df, algorithms, categories, patid_to_text_length, patid_date_to_note_count


def build_variables(data_path: pathlib.Path, meta_path: pathlib.Path, extra_condition=None, **conditions):
    (df, stacked_df, algorithms, categories,
     patid_to_text_length, patid_date_to_note_count) = prepare_datasets(
        data_path, meta_path, extra_condition=extra_condition
    )
    # create features
    features = []
    for algorithm in algorithms:
        features.append(density(f'{algorithm}', df, algorithm,
                                by_date=True,
                                normalize=patid_to_text_length,
                                ))
        features.append(density(f'{algorithm}_all', df, algorithm,
                                by_date=False,
                                normalize=patid_to_text_length,
                                ))
        if extra_condition:
            features.append(density(f'{algorithm}_{extra_condition[:4]}', df, algorithm,
                                    by_date=True,
                                    normalize=patid_to_text_length,
                                    by_extra=extra_condition,
                                    ))
            features.append(density(f'{algorithm}_all_{extra_condition[:4]}', df, algorithm,
                                    by_date=False,
                                    normalize=patid_to_text_length,
                                    by_extra=extra_condition,
                                    ))
    for category in categories:
        features.append(density(f'{category}', df, category,
                                is_algo=False,
                                by_date=True,
                                normalize=patid_to_text_length,
                                ))
        features.append(density(f'{category}_all', df, category,
                                is_algo=False,
                                by_date=False,
                                normalize=patid_to_text_length))

        if extra_condition:
            features.append(density(f'{category}_{extra_condition[:4]}', df, category,
                                    by_date=True,
                                    normalize=patid_to_text_length,
                                    by_extra=extra_condition,
                                    ))
            features.append(density(f'{category}_all_{extra_condition[:4]}', df, category,
                                    by_date=False,
                                    normalize=patid_to_text_length,
                                    by_extra=extra_condition,
                                    ))
    for name, condition in conditions.items():
        features.append(
            filter_condition(name, stacked_df, algorithms, categories, patid_to_text_length,
                             *condition,
                             extra_condition=extra_condition)
        )
    resdf = pd.DataFrame(features).T.fillna(0.0)
    resdf = resdf.reset_index()
    resdf.rename(columns={'index': 'patient_id'}, inplace=True)
    resdf = pd.merge(
        resdf,
        pd.DataFrame(patid_to_text_length.items(),
                     columns=['patient_id', 'total_text_length']),
        on='patient_id',
    )
    return resdf
