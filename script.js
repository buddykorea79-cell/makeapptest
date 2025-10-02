// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 카드 요소들 가져오기
    const cards = document.querySelectorAll('.card');
    
    // 각 카드에 클릭 이벤트 리스너 추가
    cards.forEach(card => {
        card.addEventListener('click', function() {
            // 클릭된 카드에 애니메이션 효과
            this.style.transform = 'scale(1.02)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });

    // 스크롤 애니메이션 효과
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // 카드들에 초기 스타일 설정 및 관찰 시작
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = `all 0.5s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // 페이지 로드 시 부드러운 등장 효과
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    // 스크롤 시 헤더 배경 변화
    let lastScroll = 0;
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        const header = document.querySelector('header');
        
        if (currentScroll > 100) {
            header.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.2)';
        } else {
            header.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        }
        
        lastScroll = currentScroll;
    });

    // 절감 효과 강조 애니메이션
    const highlights = document.querySelectorAll('.card-detail strong');
    highlights.forEach(highlight => {
        highlight.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
            this.style.transform = 'scale(1.1)';
            this.style.display = 'inline-block';
        });
        
        highlight.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // 목표 달성률 카운터 애니메이션 (선택적 기능)
    const goalElement = document.querySelector('.emphasis');
    if (goalElement) {
        const observer = new IntersectionObserver(function(entries) {
            if (entries[0].isIntersecting) {
                goalElement.style.animation = 'pulse 1s ease-in-out';
            }
        }, { threshold: 0.5 });
        
        observer.observe(goalElement);
    }
});

// CSS 애니메이션 동적 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    body {
        opacity: 0;
        transition: opacity 0.5s ease;
    }
`;
document.head.appendChild(style);
