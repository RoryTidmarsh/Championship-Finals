interface TableProps {
  loading: boolean;
  data: any;
  positionBased?: boolean;
}

function ResultsTable({
  loading = false,
  data = [],
  positionBased = true,
}: TableProps) {
  // Convert pandas JSON format to array of objects
  const convertPandasFormat = (pandasData: any) => {
    // If it's already an array, return it
    if (Array.isArray(pandasData)) {
      return pandasData;
    }

    // If it's the pandas format (object with column names as keys, each containing index-keyed values)
    if (typeof pandasData === "object" && pandasData !== null) {
      const columnNames = Object.keys(pandasData);
      const rowIndices = Object.keys(pandasData[columnNames[0]] || {});

      // Convert to array of objects
      return rowIndices.map((index) => {
        const row: Record<string, any> = {};
        columnNames.forEach((col) => {
          row[col] = pandasData[col][index];
        });
        return row;
      });
    }

    return [];
  };

  // Get rows in array format
  const rows = convertPandasFormat(data);

  // Get column names from first row
  const colNames = rows.length > 0 ? Object.keys(rows[0]) : [];

  return (
    <>
      <table className="table">
        <thead>
          <tr>
            {colNames.map((column) => (
              <th key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {colNames.map((colName) => (
                <td key={colName}>{row[colName]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

export default ResultsTable;
