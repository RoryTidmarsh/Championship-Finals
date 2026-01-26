interface TableProps {
  loading: boolean;
  columns: Array<string>;
  data: { rows: Array<{ id: number; name: string; value: number }> };
  positionBased: boolean;
}

function ResultsTable() {
  //   {
  //   loading = false,
  //   columns = [],
  //   data = { rows: [{ id: 1, name: "Sample", value: 100 }] },
  //   positionBased = true,
  //   }: TableProps,
  //   loading;
  //   columns;
  //   data;
  //   positionBased;
  return (
    <>
      <p>Table</p>
    </>
  );
}

export default ResultsTable;
