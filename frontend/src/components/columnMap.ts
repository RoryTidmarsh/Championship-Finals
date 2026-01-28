const columnMap = {
    'Rank_jumping': 'Jumping Rank',
    'Name': 'Name',
    'Faults_jumping': 'Jumping Faults',
    'Time_jumping': 'Jumping Time',
    'Rank_agility': 'Agility Rank',
    'Faults_agility': 'Agility Faults',
    'Time_agility': 'Agility Time',
    'Combined_Points': 'Total Points',
    'Combined_Faults': 'Total Faults',
    'Combined_Time': 'Total Time'
};

// Mobile-friendly shortened column names with line breaks for compact display
const columnMapMobile = {
    'Rank_jumping': 'Jmp\nRank',
    'Name': 'Name',
    'Faults_jumping': 'Jmp\nFaults',
    'Time_jumping': 'Jmp\nTime',
    'Rank_agility': 'Ag\nRank',
    'Faults_agility': 'Ag\nFaults',
    'Time_agility': 'Ag\nTime',
    'Combined_Points': 'Total',
    'Combined_Faults': 'Tot\nFaults',
    'Combined_Time': 'Tot\nTime'
};

type ColumnKey = keyof typeof columnMap;

export function getReadableColumnName(apiName: string, isMobile: boolean = false): string {
    const map = isMobile ? columnMapMobile : columnMap;
    return map[apiName as ColumnKey] || apiName;
}
