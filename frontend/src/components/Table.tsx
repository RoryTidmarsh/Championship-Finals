interface TableProps {
  loading: boolean;
  columns: Array<string>;
  data: { rows: Array<{ id: number; name: string; value: number }> };
  positionBased?: boolean;
}

function ResultsTable({
  loading = false,
  columns = [],
  data = { rows: [{ id: 1, name: "Sample", value: 100 }] },
  positionBased = true,
}: TableProps) {
  return (
    <>
      <p>Table</p>
      <p>{loading}</p>
      <p>{columns}</p>
    </>
  );
}

export default ResultsTable;
