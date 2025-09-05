import pandas as pd
import glob
import os

def extract_user_data_and_save(input_dir, output_dir, user_id, start_date, end_date, time_column="Time"):
    """
    Extract user data from multiple CSV files in a given directory within a date range
    and save filtered results into a new directory.

    Parameters:
    ----------
    input_dir : str
        Path to the directory containing CSV files.
    output_dir : str
        Path to the directory where filtered files will be saved.
    user_id : str or int
        The target user_id to filter.
    start_date : str
        Start date in format 'YYYY-MM-DD'.
    end_date : str
        End date in format 'YYYY-MM-DD'.
    time_column : str, optional (default="Time")
        Preferred time column in the CSV files ("Time" or "ActivityDateTime").

    Returns:
    -------
    None
    """

    # Create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # Collect all CSV files in the input directory
    all_files = glob.glob(os.path.join(input_dir, "*.csv"))

    for file in all_files:
        print("Extracting user data from {}".format(file))
        try:
            # Read CSV
            df = pd.read_csv(file)

            # Decide which time column to use
            if time_column not in df.columns:
                if "ActivityDateTime" in df.columns:
                    time_column_in_file = "ActivityDateTime"
                elif "Time" in df.columns:
                    time_column_in_file = "Time"
                elif "ActivityMinute" in df.columns:
                    time_column_in_file = "ActivityMinute"
                else:
                    print(f"Skipping {file}: No valid time column found.")
                    continue
            else:
                time_column_in_file = time_column

            # Ensure the time column is in datetime format
            df[time_column_in_file] = pd.to_datetime(df[time_column_in_file])

            # Filter by user_id and date range
            filtered = df[
                (df["Id"] == user_id) &
                (df[time_column_in_file] >= pd.to_datetime(start_date)) &
                (df[time_column_in_file] <= pd.to_datetime(end_date))
            ]


            if not filtered.empty:
                # Generate output filename
                filename = os.path.basename(file)  # original filename
                output_filename = f"user_{user_id}_{filename}"
                output_path = os.path.join(output_dir, output_filename)

                # Save to new CSV
                filtered.to_csv(output_path, index=False)
                print(f"Saved filtered file: {output_path}")

        except Exception as e:
            print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    extract_user_data_and_save(
        input_dir="../FitbitData/mturkfitbit_export_3.12.16-4.11.16/Fitabase Data 3.12.16-4.11.16",
        output_dir="../activity_data_user_5577150313/",
        user_id=5577150313,
        start_date="2016-04-01",
        end_date="2025-04-10",
        time_column="Time"  # Preferred, but will fall back to ActivityDateTime
    )
