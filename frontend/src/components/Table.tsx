import { getReadableColumnName } from "./columnMap";
import { useState, useEffect } from "react";

interface TableProps {
  data: any;
  positionBased?: boolean;
  agilityWinner?: string;
  jumpingWinner?: string;
}

function ResultsTable({
  data = [],
  positionBased = true,
  agilityWinner = "",
  jumpingWinner = "",
}: TableProps) {
  // Track if we're on mobile - initialize with current window width if available
  const [isMobile, setIsMobile] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth <= 768;
    }
    return false;
  });

  useEffect(() => {
    // Throttle resize handler to prevent excessive re-renders
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    
    const checkMobile = () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      timeoutId = setTimeout(() => {
        setIsMobile(window.innerWidth <= 768);
      }, 150);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => {
      window.removeEventListener('resize', checkMobile);
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, []);

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

  // Determine columns and sort based on positionBased prop
  let displayedCols: string[];
  let sortedRows: typeof rows;

  if (positionBased) {
    // Position-based: show ranks, sort by Combined_Points, then by Rank_agility
    displayedCols = ["Name", "Rank_jumping", "Rank_agility", "Combined_Points"];
    sortedRows = [...rows].sort((a, b) => {
      const pointsA = parseFloat(a["Combined_Points"]);
      const pointsB = parseFloat(b["Combined_Points"]);

      // Primary sort: by combined points
      if (pointsA !== pointsB) {
        return pointsA - pointsB;
      }

      // Tiebreaker: if points are equal, better agility rank goes first
      const agilityRankA = parseFloat(a["Rank_agility"]);
      const agilityRankB = parseFloat(b["Rank_agility"]);
      return agilityRankA - agilityRankB;
    });
  } else {
    // Faults-based: show faults, sort by Combined_Faults, then by Combined_Time, then by Rank_agility
    displayedCols = [
      "Name",
      "Faults_jumping",
      "Time_jumping",
      "Faults_agility",
      "Time_agility",
      "Combined_Faults",
      "Combined_Time",
    ];
    sortedRows = [...rows].sort((a, b) => {
      const faultsA = parseFloat(a["Combined_Faults"]);
      const faultsB = parseFloat(b["Combined_Faults"]);

      // Primary sort: by faults
      if (faultsA !== faultsB) {
        return faultsA - faultsB;
      }

      // Secondary sort: if faults are equal, sort by time
      const timeA = parseFloat(a["Combined_Time"]);
      const timeB = parseFloat(b["Combined_Time"]);
      if (timeA !== timeB) {
        return timeA - timeB;
      }

      // Tertiary sort: if both faults and time are equal, better agility rank goes first
      const agilityRankA = parseFloat(a["Rank_agility"]);
      const agilityRankB = parseFloat(b["Rank_agility"]);
      return agilityRankA - agilityRankB;
    });
  }

  return (
    <div className="table-container">
      <table className={positionBased ? "" : "faults-time-table"}>
        <thead>
          <tr>
            <th>Place</th>
            {displayedCols.map((column) => (
              <th key={column}>{getReadableColumnName(column, isMobile)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedRows.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className={`
                ${
                  row["Name"] === agilityWinner
                    ? "ag-win"
                    : row["Name"] === jumpingWinner
                      ? "jmp-win"
                      : rowIndex === 19
                        ? "cut-off"
                        : ""
                }
              `.trim()}
            >
              <td>{rowIndex + 1}</td>
              {displayedCols.map((colName) => (
                <td key={colName}>{row[colName]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ResultsTable;
