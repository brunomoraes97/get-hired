function createExperienceFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'experience-item';
    wrapper.innerHTML = `
        <input type="text" placeholder="Period" class="period">
        <input type="text" placeholder="Title" class="title">
        <input type="text" placeholder="Company" class="company">
        <input type="text" placeholder="Location" class="location">
        <textarea placeholder="Description" class="description"></textarea>
    `;
    return wrapper;
}

document.getElementById('addExperience').addEventListener('click', () => {
    document.getElementById('experienceContainer').appendChild(createExperienceFields());
});

function createEducationFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'education-item';
    wrapper.innerHTML = `
        <input type="text" placeholder="Period" class="period">
        <input type="text" placeholder="Degree" class="degree">
        <input type="text" placeholder="Institution" class="institution">
        <input type="text" placeholder="Field of Study" class="field">
        <textarea placeholder="Description" class="description"></textarea>
    `;
    return wrapper;
}

document.getElementById('addEducation').addEventListener('click', () => {
    document.getElementById('educationContainer').appendChild(createEducationFields());
});

function createLanguageFields() {
    const wrapper = document.createElement('div');
    wrapper.className = 'language-item';
    wrapper.innerHTML = `
        <input type="text" placeholder="Language" class="language">
        <input type="text" placeholder="Level" class="level">
    `;
    return wrapper;
}

document.getElementById('addLanguage').addEventListener('click', () => {
    document.getElementById('languageContainer').appendChild(createLanguageFields());
});

function gatherData() {
    const experiences = [];
    document.querySelectorAll('#experienceContainer .experience-item').forEach(item => {
        experiences.push({
            period: item.querySelector('.period').value,
            title: item.querySelector('.title').value,
            company: item.querySelector('.company').value,
            location: item.querySelector('.location').value,
            description: item.querySelector('.description').value,
        });
    });

    const education = [];
    document.querySelectorAll('#educationContainer .education-item').forEach(item => {
        education.push({
            period: item.querySelector('.period').value,
            degree: item.querySelector('.degree').value,
            institution: item.querySelector('.institution').value,
            field_of_study: item.querySelector('.field').value,
            description: item.querySelector('.description').value,
        });
    });

    const languages = [];
    document.querySelectorAll('#languageContainer .language-item').forEach(item => {
        const lang = item.querySelector('.language').value;
        const level = item.querySelector('.level').value;
        if (lang) languages.push(`${lang} (${level})`);
    });

    return {
        name: document.getElementById('name').value,
        location: document.getElementById('location').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        summary: document.getElementById('summary').value,
        skills: document.getElementById('skills').value.split(',').map(s => s.trim()).filter(s => s),
        experiences: experiences,
        education: education,
        languages: languages
    };
}

document.getElementById('builderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = gatherData();
    const response = await fetch('/create-resume', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume.pdf';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } else {
        alert('Error generating resume');
    }
});
