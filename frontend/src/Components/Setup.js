

import { React, useState } from 'react';

import { Form, FormGroup, Label, Input, Button } from 'reactstrap';


// A component that will be used to set up a new game.
const Setup = () => {

    const [theme, setTheme] = useState('');
    const [details, setDetails] = useState('');
    const [timeframe, setTimeframe] = useState('');
  


    // to add - useffect, to run to initialize game key, when component is first rendered


    const handleSubmit = (e) => {
        e.preventDefault();
        // Handle form submission logic here
        console.log('Theme:', theme);
        console.log('Details:', details);
        console.log('Timeframe:', timeframe);
      };



    return (
        <div className='container flex-column'
        style={{ height: '90%', width: '90%', 
            border: '1px white solid',
        }}>
            <Form onSubmit={handleSubmit}>
                <FormGroup>
                <Label className='text' for="theme">Theme:</Label>
                <Input
                    type="text"
                    name="theme"
                    id="theme"
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                />
                </FormGroup>
                <FormGroup>
                <Label className='text' for="details">Details:</Label>
                <Input
                    type="textarea"
                    name="details"
                    id="details"
                    value={details}
                    onChange={(e) => setDetails(e.target.value)}
                />
                </FormGroup>
                <FormGroup>
                <Label className='text' for="timeframe">Timeframe:</Label>
                <Input
                    type="text"
                    name="timeframe"
                    id="timeframe"
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                />
                </FormGroup>
        <Button type="submit">Submit</Button>
      </Form>
        </div>
    )


};

export default Setup;