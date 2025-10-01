import { SUPABASE_URL, SUPABASE_ANON_KEY } from './config.js';
// Supabase 클라이언트 라이브러리를 CDN에서 ES 모듈로 가져옵니다.
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

// 1. Supabase 클라이언트 초기화
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Supabase에서 Iris 데이터를 가져와 Plotly.js를 사용하여 산점도를 시각화합니다.
 */
async function visualizeIrisData() {
    const chartContainer = document.getElementById('chart-container');
    const loadingMessage = document.getElementById('loading-message');
    
    if (loadingMessage) {
        loadingMessage.style.display = 'block'; // 로딩 메시지 표시
    }
    
    // 2. Supabase에서 'iris' 테이블 데이터 가져오기
    const { data: irisData, error } = await supabase
        .from('iris')
        .select('sepal_length, petal_length, species');

    if (loadingMessage) {
        loadingMessage.style.display = 'none'; // 로딩 메시지 숨김
    }

    if (error) {
        chartContainer.innerHTML = `<div class="p-4 text-red-600 bg-red-100 rounded-lg">데이터 로드 오류: 
                                      Supabase 접속 정보를 확인하거나, 'iris' 테이블과 RLS(Row Level Security) 설정을 확인해주세요.<br>
                                      오류 메시지: ${error.message}</div>`;
        console.error('Supabase 데이터 로드 중 오류 발생:', error);
        return;
    }

    if (!irisData || irisData.length === 0) {
        chartContainer.innerHTML = '<div class="p-4 text-gray-600">데이터가 없습니다. Supabase 테이블을 확인해주세요.</div>';
        return;
    }

    // 3. Plotly를 위한 데이터 구조화 (종(species)별로 분리하여 트레이스 생성)
    const speciesGroups = {};
    irisData.forEach(row => {
        const species = row.species || 'Unknown';
        if (!speciesGroups[species]) {
            speciesGroups[species] = {
                x: [], // sepal_length (꽃받침 길이)
                y: [], // petal_length (꽃잎 길이)
                mode: 'markers',
                type: 'scatter',
                name: species,
                marker: { size: 10, opacity: 0.8 }
            };
        }
        speciesGroups[species].x.push(row.sepal_length);
        speciesGroups[species].y.push(row.petal_length);
    });

    const plotData = Object.values(speciesGroups);

    // 4. 시각화 레이아웃 설정
    const layout = {
        title: {
            text: 'Iris 데이터셋 시각화: Sepal Length vs Petal Length',
            font: { size: 20, color: '#333' }
        },
        xaxis: { title: 'Sepal Length (꽃받침 길이, cm)' },
        yaxis: { title: 'Petal Length (꽃잎 길이, cm)' },
        hovermode: 'closest',
        responsive: true,
        height: 600,
        margin: { t: 50, b: 50, l: 50, r: 50 }
    };

    // 5. 차트 렌더링
    // Plotly.newPlot(DOM 요소, 데이터, 레이아웃, 설정)
    Plotly.newPlot(chartContainer, plotData, layout, { 
        responsive: true, // 반응형 차트 활성화
        displayModeBar: false // 상단 툴바 숨김
    });
}

// DOM 로드 후 애플리케이션 시작
window.onload = visualizeIrisData;
