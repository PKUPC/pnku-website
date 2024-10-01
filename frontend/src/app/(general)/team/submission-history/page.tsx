import { DownloadOutlined } from '@ant-design/icons';
import { Button } from 'antd';

import PassedPlot from '@/app/(general)/team/submission-history/PassedPlot.tsx';
import { TeamSubmissionList } from '@/app/(general)/team/submission-history/TeamSubmissionList';
import { Loading } from '@/components/DaisyUI/Loading.tsx';
import { WishError } from '@/components/WishError.tsx';
import { useWishData } from '@/logic/swrWrappers';
import { Wish } from '@/types/wish.ts';
import { format_ts } from '@/utils.ts';

function genCSV(data: Wish.Team.TeamSubmissionInfo[]) {
    const header = ['提交时间', '题目', '提交人', '提交内容', '状态', '信息'].join(',') + '\n';
    const rows = data
        .map((item) => {
            const timeStr = format_ts(item.timestamp_s);
            let content = item.origin;
            if (content.includes('"')) content = content.replace(/"/g, '""');
            if (content.includes('\n')) content = content.replaceAll('\n', '\\n');
            if (content.includes(',') || content.includes('"')) content = `"${content}"`;
            return [timeStr, item.puzzle, item.user_name, content, item.status, item.info].join(',');
        })
        .join('\n');
    return header + rows;
}

export function SubmissionHistoryPage() {
    const { data } = useWishData({
        endpoint: 'team/get_submission_history',
        payload: undefined,
    });

    if (!data) return <Loading />;
    if (data.status === 'error') return <WishError res={data} />;

    return (
        <div>
            {data.data.passed_submissions.length > 0 && <PassedPlot passedSubmissions={data.data.passed_submissions} />}

            <br />
            <TeamSubmissionList submissions={data.data.submissions} />
            <br />
            <div style={{ textAlign: 'right' }}>
                <Button
                    onClick={() => {
                        const csvContent = genCSV(data.data.submissions);
                        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.setAttribute('href', url);
                        link.setAttribute('download', 'submissions.csv');
                        link.style.visibility = 'hidden';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }}
                >
                    <DownloadOutlined />
                    存储为 csv 文件
                </Button>
            </div>
        </div>
    );
}
