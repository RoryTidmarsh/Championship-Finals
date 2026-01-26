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

export function getReadableColumnName(apiName: string): string {
    return columnMap[apiName as keyof typeof columnMap] || apiName;
}
