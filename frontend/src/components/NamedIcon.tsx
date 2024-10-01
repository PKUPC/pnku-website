import { AimOutlined, FundOutlined, QuestionCircleOutlined, ThunderboltOutlined } from '@ant-design/icons';

import { BuildingIcon, InstructionIcon, VacationIcon } from '@/SvgIcons';

export default function NamedIcon({ iconName }: { iconName: string }) {
    switch (iconName) {
        case 'ranking':
            return <FundOutlined />;
        case 'first-blood':
            return <AimOutlined />;
        case 'building':
            return <BuildingIcon />;
        case 'instruction':
            return <InstructionIcon />;
        case 'vacation':
            return <VacationIcon />;
        case 'thunder':
            return <ThunderboltOutlined />;
        default:
            return <QuestionCircleOutlined />;
    }
}
