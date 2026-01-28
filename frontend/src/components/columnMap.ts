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

// Mobile-friendly shortened column names
const columnMapMobile = {
    'Rank_jumping': 'Jmp Rank',
    'Name': 'Name',
    'Faults_jumping': 'Jmp Faults',
    'Time_jumping': 'Jmp Time',
    'Rank_agility': 'Ag Rank',
    'Faults_agility': 'Ag Faults',
    'Time_agility': 'Ag Time',
    'Combined_Points': 'Total',
    'Combined_Faults': 'Tot Faults',
    'Combined_Time': 'Tot Time'
};

type ColumnKey = keyof typeof columnMap;

export function getReadableColumnName(apiName: string, isMobile: boolean = false): string {
    const map = isMobile ? columnMapMobile : columnMap;
    return map[apiName as ColumnKey] || apiName;
}
