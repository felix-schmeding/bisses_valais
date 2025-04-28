import pandas as pd

def resolve_values(val_after, next_val_before, prio='debut_fin'):
    if pd.isna(val_after):
        return next_val_before
    elif pd.isna(next_val_before):
        return val_after
    else:
        if prio == 'debut_fin':
            return next_val_before
        if prio == 'fin_debut':
            return val_after  

def create_sections(meas_df, col_names=['val_av', 'val_ap'], prio='debut_fin'):
    # Ensure the DataFrame is sorted by distance
    meas_df = meas_df.sort_values('dist_m').reset_index(drop=True)

    avant = col_names[0]
    apres = col_names[1]
    # Ensure None are recognized as NaN for pandas
    meas_df[avant] = meas_df[avant].astype('object')
    meas_df[apres] = meas_df[apres].astype('object')

    meas_df['next_val_before'] = meas_df[avant].shift(-1)
    meas_df['discrepancy'] = meas_df[apres] != meas_df['next_val_before']  

    mask = meas_df['discrepancy']  
    
    # Apply resolution
    resolved_vals = [
        resolve_values(a, b, prio)
        for a, b in zip(meas_df.loc[mask, apres], meas_df.loc[mask, 'next_val_before'])
    ]

    # Assign fixed values
    meas_df.loc[mask, apres] = resolved_vals

    # Assign to val_before of next row (shift mask and resolved_vals accordingly)
    next_mask = mask.shift(1, fill_value=False)
    resolved_vals_for_next = resolved_vals[:len(meas_df.loc[next_mask])]
    meas_df.loc[next_mask, avant] = resolved_vals_for_next

    # meas_df.drop(columns=['next_val_before', 'discrepancy'], inplace=True)

    # * maybe seperate in another function
    df = meas_df.copy()

    sections = []
    current_value = df.loc[0, apres]
    start_dist = df.loc[0, 'dist_m']
    comments = []
    
    #for i in range(1, len(df)):
    for i, row in df.iloc[1:,:].iterrows():
        current_after = row[apres]

        comments.append(row['comment'])
        
        # If value changes, close the current section
        if current_after != current_value:
            end_dist = row['dist_m']

            section = {
                'value': current_value,
                'start_dist_m': start_dist,
                'end_dist_m': end_dist,
                'comment': comments
            }
            sections.append(section)
            
            # Start new section
            current_value = current_after
            start_dist = end_dist
            comments = []

    # Add the final section (up to the last point)
    section = {
        'value': current_value,
        'start_dist_m': start_dist,
        'end_dist_m': df.loc[len(df) - 1, 'dist_m'],
        'comment': comments

    }
    sections.append(section)
    
    return pd.DataFrame(sections)