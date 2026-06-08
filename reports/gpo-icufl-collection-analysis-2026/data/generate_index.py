import pathlib
import zipfile
import json
import csv
import pyarrow as pa
import pyarrow.parquet as pq

icufl_lsjson = "gpo.lsjson"
icufl_items_csv = "gpo-icufl-items.csv"
idx_zip = "local.zip"
parquet_items = "gpo-icufl-items.parquet"
parquet_file = "gpo-icufl-files.parquet"

# Load Items metadata and assemble mapping 
# of img/iso to item_id + FID:
# ---------------------------------------
items = []
with open(icufl_items_csv) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        items.append(row)

files_to_items = {}
files_to_fids = {}
for item in items:
    fids = item["fids"].split("|")
    fnames = item["fnames"].split("|")
    for i in range(0, len(fids)):
        fid = fids[i]
        fname = fnames[i]
        files_to_items[fname] = int(item["item_id"])
        files_to_fids[fname] = fid

# -------------------------------------------------------------
# A helper class to write a Parquet file from a stream of dicts.
# Using small batch_size will limit the maximum Parquet page size.
# The syntax for sorting is like: sort_order = [('id', 'ascending')]
# -------------------------------------------------------------
class ParquetDictWriter(object):
    def __init__(self, file_name, compression="snappy", batch_size=1_048_576, sort_order=None):
        self.file_name = file_name
        self.compression = compression
        self.batch_size = batch_size
        self.sort_order = sort_order

    def __enter__(self):
        self.batch = []
        self.counter = 0
        self.schema = None
        self.writer = None
        return self
    
    def _init_writer(self, item):
        table = pa.Table.from_struct_array(pa.array([item]))
        self.schema = table.schema
        # Sorting, if set:
        sorting_columns= None
        if self.sort_order:
            sorting_columns = pq.SortingColumn.from_ordering(self.schema, self.sort_order)
        # Open a Parquet file for writing
        self.writer = pq.ParquetWriter(
            self.file_name, self.schema, 
            compression=self.compression, 
            write_page_index=True, 
            sorting_columns=sorting_columns
        )

    def _write_batch(self):
        # Write chunk to the parquet file
        table = pa.Table.from_struct_array(pa.array(self.batch))
        # Sort the data, if requested:
        if self.sort_order:
            table = table.sort_by(self.sort_order)
        # And write:
        self.writer.write_table(table)
        self.batch = []

    def write(self, item):
        self.counter += 1
        if self.writer == None:
            self._init_writer(item)
        # Process in chunks
        if self.counter % self.batch_size == 0:
            self._write_batch()
        else:
            self.batch.append(item)

    def __exit__(self, type, value, traceback):
        if len(self.batch) > 0:
            self._write_batch()
        # And close:
        self.writer.close()



# Build up index of files in items
with ParquetDictWriter(parquet_file, 
                       compression="brotli", 
                       sort_order=[('item_id', 'ascending'),('extension', 'ascending')]) as pw:
    with zipfile.ZipFile(idx_zip, "r") as f:
        for entry in f.infolist():
            # Skip directories:
            if entry.is_dir():
                continue
            # Only open .idx files:
            name = entry.filename
            if name.endswith(".idx"):
                # Open as Zip objects:
                with f.open(name) as z:
                    # Read in lines:
                    for line in z:
                        # Skip comments:
                        if line.startswith(b"#"):
                            continue
                        # Parse lines:
                        line = line.strip()
                        parts = line.split(b"|")
                        file_path = pathlib.Path(name)
                        item_name = parts[0].decode()
                        item_path = pathlib.Path(item_name)
                        media_file = file_path.name[:-4]  # Drop the '.idx' bit
                        item_id = files_to_items.get(media_file, None)
                        fid = files_to_fids.get(media_file, None)
                        item = {
                            "item_id": item_id,
                            "media": media_file,
                            "fid": fid,
                            "path": item_name,
                            "extension": item_path.suffix,
                            "size": int(parts[1]),
                            "timestamp": int(parts[2]),
                            "type": parts[3].decode(),
                            "chunks": parts[4].decode(),
                        }
                        pw.write(item)

