exports.handler = async event => {
    const { Name } = JSON.parse(event.body);
  
    return {
      statusCode: 200,
      body: `\n\nHi ${Name} \n\n`
    };
  };