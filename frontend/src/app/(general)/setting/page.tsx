import { Alert, Radio } from 'antd';
import { useContext } from 'react';

import FancyCard from '@/components/FancyCard';
import { InputWithLabel } from '@/components/InputWithLabel.tsx';
import { SiteSettingContext } from '@/logic/contexts.ts';

export function SettingPage() {
    const { usePuzzleList, setUsePuzzleList } = useContext(SiteSettingContext);
    const { theme, setTheme } = useContext(SiteSettingContext);

    return (
        <div className={'slim-container'}>
            <Alert
                type={'info'}
                showIcon={true}
                message={'设置保存在本地，清除浏览器数据或者切换浏览器会丢失设置。'}
                style={{ marginBottom: 16, marginTop: 16 }}
            />
            <FancyCard title="外观设置">
                <InputWithLabel label={'颜色模式'}>
                    <Radio.Group value={theme} onChange={(e) => setTheme(e.target.value)}>
                        <Radio.Button value="light">浅色模式</Radio.Button>
                        <Radio.Button value="dark">深色模式</Radio.Button>
                        <Radio.Button value="system">跟随系统</Radio.Button>
                    </Radio.Group>
                </InputWithLabel>
                <br />
                <InputWithLabel
                    label={'谜题页显示谜题列表'}
                    extra={<>谜题页将显示该题所在谜题组的题目列表，也许有人觉得这样更方便。</>}
                >
                    <Radio.Group value={usePuzzleList} onChange={(e) => setUsePuzzleList(e.target.value)}>
                        <Radio.Button value="off">不显示</Radio.Button>
                        <Radio.Button value="show">总是显示</Radio.Button>
                        {/* <Radio.Button value="drawer">放入折叠侧栏</Radio.Button> */}
                    </Radio.Group>
                </InputWithLabel>
            </FancyCard>
        </div>
    );
}
