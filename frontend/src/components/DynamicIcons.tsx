import { BorderOutlined, CheckSquareTwoTone, LockOutlined, MinusSquareOutlined } from '@ant-design/icons';

import { PnKU3Day3Icon } from '@/SvgIcons';
import { useTheme } from '@/logic/contexts.ts';

export function PuzzleIcon({ status }: { status: 'untouched' | 'partial' | 'passed' | 'found' }) {
    const { color } = useTheme();

    if (status === 'untouched') return <BorderOutlined style={{ opacity: 0.3 }} />;
    else if (status === 'partial') return <MinusSquareOutlined style={{ opacity: 0.3 }} />;
    else if (status === 'passed') {
        return <CheckSquareTwoTone twoToneColor={[color.success, color.base100]} />;
    } else if (status === 'found') {
        return <LockOutlined style={{ opacity: 0.3 }} />;
    } else if (status === 'special') {
        return <PnKU3Day3Icon style={{ transform: 'scale(1.4)', opacity: 0.6 }} />;
    } else return 'never';
}
